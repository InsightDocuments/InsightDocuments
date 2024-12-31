import React, { useState } from "react";
import axios from "axios";

const SearchBar = () => {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");

    const handleInputChange = (event) => {
        setQuery(event.target.value);
    };

const handleSearch = async () => {
    if (!query) {
        setResponse("Please enter a query.");
        return;
    }

    try {
        const res = await axios.post("http://127.0.0.1:5000/query", {
            question: query,
        });
        setResponse(`Answer: ${res.data.answer}\nReference: ${res.data.reference}`);
    } catch (error) {
        setResponse("Error: Unable to process your query. Please try again later.");
    }
};

    return (
        <div>
            <h2>Search Your Document</h2>
            <input
                type="text"
                value={query}
                onChange={handleInputChange}
                placeholder="Enter your question here"
                style={{ width: "300px", padding: "5px" }}
            />
            <button onClick={handleSearch} style={{ marginLeft: "10px", padding: "5px" }}>
                Search
            </button>
            {response && <p>{response}</p>}
        </div>
    );
};

export default SearchBar;