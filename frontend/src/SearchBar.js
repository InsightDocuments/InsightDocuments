import React, { useState } from 'react';
import axios from 'axios';

const SearchBar = () => {
    const [question, setQuestion] = useState(''); // State for user input
    const [response, setResponse] = useState(null); // State for API response
    const [error, setError] = useState(null); // State for errors

    const handleSearch = async () => {
        try {
            setError(null); // Clear previous errors
            const res = await axios.post('http://127.0.0.1:5000/query', {
                question: question,
            });
            setResponse(res.data); // Save response to state
        } catch (err) {
            setError('Error querying the backend. Please try again.');
            console.error(err);
        }
    };

    return (
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <h2>Ask a Question</h2>
            <input
                type="text"
                placeholder="Enter your question here"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                style={{
                    width: '300px',
                    padding: '10px',
                    marginBottom: '10px',
                }}
            />
            <br />
            <button
                onClick={handleSearch}
                style={{
                    padding: '10px 20px',
                    fontSize: '16px',
                    cursor: 'pointer',
                }}
            >
                Search
            </button>
            <div style={{ marginTop: '20px' }}>
                {response && (
                    <div>
                        <p>
                            <strong>Answer:</strong> {response.answer}
                        </p>
                        <p>
                            <strong>Reference:</strong> {response.reference}
                        </p>
                    </div>
                )}
                {error && <p style={{ color: 'red' }}>{error}</p>}
            </div>
        </div>
    );
};

export default SearchBar;