import "./App.css";
import React from "react";
import FileUpload from "./FileUpload";
import SearchBar from "./SearchBar";

const App = () => {
    return (
        <div className="App">
            <h1>InsightDocuments</h1>
            <FileUpload />
            <hr style={{ margin: "20px 0" }} />
            <SearchBar />
        </div>
    );
};

export default App;