import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [message, setMessage] = useState("");

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleFileUpload = async () => {
        if (!selectedFile) {
            setMessage("Please select a file to upload.");
            return;
        }
    
        const formData = new FormData();
        formData.append("file", selectedFile);
    
        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData);
            if (response.status === 200) {
                setMessage("File uploaded successfully!");
            } else {
                setMessage("Failed to upload file. Please try again.");
            }
        } catch (error) {
            setMessage("Failed to upload file. Please try again.");
            console.error("Error uploading file:", error);
        }
    };

    return (
        <div>
            <h2>Upload a PDF</h2>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleFileUpload}>Upload</button>
            <p>{message}</p>
        </div>
    );
};

export default FileUpload;