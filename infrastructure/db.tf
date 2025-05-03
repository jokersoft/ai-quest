resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "${var.name}-aurora-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "${var.name}-aurora-subnet-group"
  }
}

resource "aws_security_group" "aurora_sg" {
  name        = "${var.name}-aurora-sg"
  description = "Security group for Aurora database"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 3306 # (MySQL)
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  # DatabaseName must begin with a letter and contain only alphanumeric characters.
  db_name = replace(var.name, "-", "")
}

# Aurora cluster configuration
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier      = var.name
  engine                  = "aurora-mysql"
  engine_version          = "8.0"
  engine_mode             = "provisioned"  # Serverless v2 uses provisioned mode
  database_name           = local.db_name
  master_username         = local.secrets["db-username"]
  master_password         = local.secrets["db-password"]
  db_subnet_group_name    = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids  = [aws_security_group.aurora_sg.id]

  # Cost optimization settings
  backup_retention_period = 1                # Minimum for cost saving
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = true             # For dev/test environments
  apply_immediately       = true
  deletion_protection     = false            # For easy cleanup in dev/test

  # Serverless v2 scaling configuration
  serverlessv2_scaling_configuration {
    min_capacity = 0.5  # Minimum ACU (can scale down during idle periods)
    max_capacity = 1.0  # Maximum ACU (increase based on your workload needs)
  }
}

resource "aws_rds_cluster_instance" "aurora_instances" {
  count               = 1                    # Single instance for minimum cost
  identifier          = "${var.name}-instance-${count.index}"
  cluster_identifier  = aws_rds_cluster.aurora_cluster.id
  instance_class      = "db.serverless"  # Required for Serverless v2
  engine              = aws_rds_cluster.aurora_cluster.engine
  engine_version      = aws_rds_cluster.aurora_cluster.engine_version
  publicly_accessible = false
}
