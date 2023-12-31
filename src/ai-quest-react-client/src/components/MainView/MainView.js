import React from 'react';
import './MainView.css';

class MainView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            threadId: localStorage.getItem('threadId') || '',
            runId: localStorage.getItem('runId') || '',
            runStatus: localStorage.getItem('runStatus') || '',
            message: '',
            messages: [],
            isLoading: false
        };
        this.messageEndRef = React.createRef();
        this.inputFieldRef = React.createRef();
    }

    componentDidMount() {
        console.log('componentDidMount');

        const { threadId, runId, runStatus } = this.state;
        if (threadId && runId && runStatus) {
            this.fetchMessages();
        }
    }

    componentDidUpdate(prevProps, prevState) {
        console.log('componentDidUpdate');
        // handle state changes.
    }

    scrollToBottom = () => {
        this.messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    handleInputChange = (event) => {
        console.log('handleInputChange');
        const { name, value } = event.target;
        this.setState({ [name]: value });

        if (['threadId', 'runId', 'runStatus'].includes(name)) {
            localStorage.setItem(name, value);
        }
    };

    renderLoader = () => {
        return (
            <div className="loader"></div>
            );
    };

    startNewGame = async () => {
        console.log('startNewGame');
        const initTimeout = 5000;
        const url = 'http://localhost:8000/api/v1/init/';
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log('init response:');
            console.log(data);

            this.setState({
                runId: data.run_id,
                runStatus: data.run_status,
                threadId: data.thread_id
            })
        })
        .then(data => {
            setTimeout(function() {
                this.fetchMessages();
            }, initTimeout);
        });
    };

    submitForm = async () => {
        console.log('submitForm');
        this.setState({ isLoading: true });
        const pollTimeout = 5000;
        const url = 'http://localhost:8000/api/v1/action/';
        let data = {
            message: this.state.message,
            thread_id: this.state.threadId,
        };

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(response => {
                console.log('response');
                console.log(response);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('action response data:');
                console.log(data);
                this.setState({
                    runId: data.run_id,
                    runStatus: data.run_status,
                    message: '',
                    isLoading: false
                }, () => {
                    this.inputFieldRef.current?.focus();
                })
                setTimeout(async () => {
                    await this.pollRun(this.fetchMessages);
                }, pollTimeout);
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
                this.setState({ isLoading: false });
            });
    };

    fetchMessages = () => {
        console.log('fetchMessages');
        this.setState({ isLoading: true });
        const threadId = this.state.threadId;
        const url = 'http://localhost:8000/api/v1/messages/' + threadId;

        fetch(url)
            .then(response => {
                console.log('response');
                console.log(response);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('data');
                console.log(data);

                // Assuming the data returned is an object with a 'messages' array
                this.setState({
                    messages: data.messages,
                    isLoading: false
                }, this.scrollToBottom);
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
                this.setState({ isLoading: false });
            });
    }
    
    renderMessages = () => {
        const reversedMessages = [...this.state.messages].reverse();
        return reversedMessages.map((message, index) => {
            const splitMessage = message.content[0].text.value.split('\n').join('</p><p>');
            const messageClass = message.role === 'user' ? 'message-user' : '';
            return (
                <p key={index} dangerouslySetInnerHTML={{ __html: splitMessage }} className={messageClass}></p>
            );
        });
    };

    pollRun = async (callbackFunction = () => {}, retryNumber = 0) => {
        console.log(`pollRun ${retryNumber}`);
        const runPollRetries = 10;
        const pollTimeout = 5000;
    
        console.log('pollRun');
        const { threadId, runId } = this.state;
    
        setTimeout(async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/v1/threads/${threadId}/runs/${runId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                const run = await response.json();
    
                console.log('fetch result (run):');
                console.log(run);
    
                const runStatus = run.status;
                this.setState({ runStatus });
    
                if (runStatus === 'completed') {
                    console.log('poll completed!');
                    this.setState({ runId: '' });
                    callbackFunction();
                    return;
                }
                
                if (runStatus === 'requires_action') {
                    console.log('run requires_action, waiting...');
                }
    
                retryNumber++;
                if (retryNumber < runPollRetries) {
                    console.log('pollRun retryNumber: ' + retryNumber);
                    await this.pollRun(callbackFunction, retryNumber);
                }
            } catch (error) {
                console.error('An error occurred during the pollRun:', error);
            }
        }, pollTimeout);
    };

    render() {
        const { threadId, runId, runStatus, message, isLoading } = this.state;

        return (
            <div className="main-view">
                {isLoading && this.renderLoader()}
                <div id="debug">
                    <textarea
                        name="threadId"
                        value={threadId}
                        onChange={this.handleInputChange}
                        placeholder="ThreadId"
                    />
                    <textarea
                        name="runId"
                        value={runId}
                        onChange={this.handleInputChange}
                        placeholder="RunId"
                    />
                    <textarea
                        name="runStatus"
                        value={runStatus}
                        onChange={this.handleInputChange}
                        placeholder="RunStatus"
                    />
                </div>
                <div className="chat-section">
                    <div className="scrollable-text-area">
                        {this.renderMessages()}
                        <div ref={this.messageEndRef} />
                    </div>
                    <div className="input-area">
                        <textarea
                            className="input-field"
                            name="message"
                            value={message}
                            onChange={this.handleInputChange}
                            onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                                e.preventDefault();
                                this.submitForm();
                            }
                        }}
                            disabled={isLoading}
                            ref={this.inputFieldRef}
                        />
                        <button className="button" onClick={this.submitForm} disabled={isLoading}>Submit</button>
                        <button className="button" onClick={this.fetchMessages} disabled={isLoading}>Fetch</button>
                    </div>
                </div>
                <div className="user-section">
                    <button className="button" onClick={this.startNewGame} disabled={isLoading}>Start new game</button>
                </div>
            </div>
            );
    }
}
export default MainView;
