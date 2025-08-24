"""
Token Tracking for Anthropic and AWS Bedrock
Includes DynamoDB tracking, and accurate pricing
"""
import json
import logging
import datetime
from decimal import Decimal
from typing import Dict, Any, List, Literal
import uuid
import os

import boto3
from app.clients import config

logger = logging.getLogger(__name__)
config = config.Config()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock_client = boto3.client('bedrock-runtime')


class DynamoDBTokenTracker:
    """
    DynamoDB-based token tracking with accurate pricing for Frankfurt region

    Table Schema:
    - Partition Key: service_date (e.g., "anthropic#2025-01-20")
    - Sort Key: timestamp_request_id (e.g., "2025-01-20T10:30:45.123456#req-123")
    - GSI: model_index with model as partition key for model-specific queries
    """

    def __init__(self, table_name: str = None):
        self.table_name = table_name or os.environ.get('TOKEN_TRACKING_TABLE', 'llm-token-usage')
        self.table = dynamodb.Table(self.table_name)

    def track_usage(self, service: str, model: str, input_tokens: int,
                    output_tokens: int, metadata: Dict[str, Any] = None,
                    request_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """Store token usage in DynamoDB with enhanced metadata"""

        now = datetime.datetime.now(datetime.UTC)
        date_str = now.strftime('%Y-%m-%d')
        timestamp = now.isoformat()

        # Use provided request_id or generate one
        if not request_id:
            request_id = str(uuid.uuid4())[:8]

        # Calculate cost
        estimated_cost = self._calculate_cost(service, model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens

        item = {
            'service_date': f"{service}#{date_str}",
            'timestamp_request_id': f"{timestamp}#{request_id}",
            'service': service,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'timestamp': timestamp,
            'date': date_str,
            'hour': now.hour,
            'ttl': int((now + datetime.timedelta(days=90)).timestamp()),  # Auto-delete after 90 days
            'metadata': json.dumps(metadata or {}),
            'estimated_cost_usd': estimated_cost,
            'region': os.environ.get('AWS_REGION', 'eu-central-1'),
        }

        # Add optional fields
        if user_id:
            item['user_id'] = user_id

        # Add Lambda context if available
        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            item['lambda_function'] = os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
            item['lambda_request_id'] = os.environ.get('AWS_REQUEST_ID', 'unknown')

        try:
            self.table.put_item(Item=item)
            logger.info(f"Tracked {total_tokens} tokens for {service}/{model}, cost: ${estimated_cost}")
        except Exception as e:
            # Don't let tracking failures break the main flow
            logger.error(f"Failed to track token usage: {e}", exc_info=True)

        return item

    def _calculate_cost(self, service: str, model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate estimated cost based on current pricing (January 2025)

        Pricing is identical for Anthropic models whether using direct API or AWS Bedrock.
        All prices are in USD per million tokens.
        AWS Bedrock Frankfurt (eu-central-1) pricing.
        """

        # Current pricing as of January 2025 - Frankfurt region
        pricing = {
            'anthropic': {
                # Claude 4 family
                'claude-opus-4-1-20250805': {'input': 15.00, 'output': 75.00},
                'claude-opus-4-20241029': {'input': 15.00, 'output': 75.00},
                'claude-sonnet-4-20250104': {'input': 3.00, 'output': 15.00},

                # Claude 3.5 family
                'claude-3.5-sonnet-20241022': {'input': 3.00, 'output': 15.00},
                'claude-3.5-sonnet-20240620': {'input': 3.00, 'output': 15.00},
                'claude-3.5-haiku-20241022': {'input': 0.80, 'output': 4.00},

                # Claude 3 family
                'claude-3-opus-20240229': {'input': 15.00, 'output': 75.00},
                'claude-3-sonnet-20240229': {'input': 3.00, 'output': 15.00},
                'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25},

                # Legacy models
                'claude-instant-1.2': {'input': 0.80, 'output': 2.40},
                'claude-2.1': {'input': 8.00, 'output': 24.00},
                'claude-2.0': {'input': 8.00, 'output': 24.00},
            },
            'bedrock': {
                # Amazon Titan models - Frankfurt region
                'amazon.titan-embed-text-v2:0': {'input': 0.10, 'output': 0},
                'amazon.titan-embed-text-v1': {'input': 0.10, 'output': 0},
                'amazon.titan-text-lite-v1': {'input': 0.30, 'output': 0.40},
                'amazon.titan-text-express-v1': {'input': 1.30, 'output': 1.70},

                # Anthropic models via Bedrock (same pricing)
                'anthropic.claude-opus-4-1-20250805-v1:0': {'input': 15.00, 'output': 75.00},
                'anthropic.claude-opus-4-20241029-v1:0': {'input': 15.00, 'output': 75.00},
                'anthropic.claude-sonnet-4-20250104-v1:0': {'input': 3.00, 'output': 15.00},
                'anthropic.claude-3-5-sonnet-20241022-v2:0': {'input': 3.00, 'output': 15.00},
                'anthropic.claude-3-5-haiku-20241022-v1:0': {'input': 0.80, 'output': 4.00},
                'anthropic.claude-3-opus-20240229-v1:0': {'input': 15.00, 'output': 75.00},
                'anthropic.claude-3-sonnet-20240229-v1:0': {'input': 3.00, 'output': 15.00},
                'anthropic.claude-3-haiku-20240307-v1:0': {'input': 0.25, 'output': 1.25},
            }
        }

        if service in pricing and model in pricing[service]:
            rates = pricing[service][model]
            cost = (input_tokens * rates['input'] / 1_000_000) + \
                   (output_tokens * rates['output'] / 1_000_000)
            return Decimal(str(round(cost, 6)))

        # Log unknown model for debugging
        logger.warning(f"Unknown model for pricing: {service}/{model}")
        return Decimal('0')

    def get_daily_usage(self, service: str, date: str) -> List[Dict]:
        """Query usage for a specific service and date"""

        response = self.table.query(
            KeyConditionExpression='service_date = :service_date',
            ExpressionAttributeValues={
                ':service_date': f"{service}#{date}"
            }
        )

        return response.get('Items', [])

    def get_usage_by_model(self, model: str, start_date: str, end_date: str) -> List[Dict]:
        """Query usage for a specific model across date range (requires GSI)"""

        try:
            response = self.table.query(
                IndexName='model_index',
                KeyConditionExpression='model = :model AND #ts BETWEEN :start AND :end',
                ExpressionAttributeNames={
                    '#ts': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':model': model,
                    ':start': start_date,
                    ':end': end_date
                }
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error querying by model (GSI might not exist): {e}")
            return []

    def get_usage_summary(self, service: str, start_date: str, end_date: str) -> Dict:
        """Get aggregated usage summary for a date range"""

        total_input = 0
        total_output = 0
        total_cost = Decimal('0')
        request_count = 0
        model_breakdown = {}

        # Query each day in the range
        current = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            daily_usage = self.get_daily_usage(service, date_str)

            for item in daily_usage:
                input_tokens = item.get('input_tokens', 0)
                output_tokens = item.get('output_tokens', 0)
                cost = item.get('estimated_cost_usd', Decimal('0'))
                model = item.get('model', 'unknown')

                total_input += input_tokens
                total_output += output_tokens
                total_cost += cost
                request_count += 1

                # Track per-model breakdown
                if model not in model_breakdown:
                    model_breakdown[model] = {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'cost': Decimal('0'),
                        'requests': 0
                    }

                model_breakdown[model]['input_tokens'] += input_tokens
                model_breakdown[model]['output_tokens'] += output_tokens
                model_breakdown[model]['cost'] += cost
                model_breakdown[model]['requests'] += 1

            current += datetime.timedelta(days=1)

        # Convert Decimal to float for JSON serialization
        for model in model_breakdown:
            model_breakdown[model]['cost'] = float(model_breakdown[model]['cost'])

        return {
            'service': service,
            'start_date': start_date,
            'end_date': end_date,
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'estimated_cost_usd': float(total_cost),
            'request_count': request_count,
            'avg_tokens_per_request': (total_input + total_output) / request_count if request_count > 0 else 0,
            'avg_cost_per_request': float(total_cost / request_count) if request_count > 0 else 0,
            'model_breakdown': model_breakdown
        }
