import { useState } from "react";
import { api } from "../api/api";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleUpload = async () => {
    if (!file) return setMessage("Select a file first");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("Upload successful: " + response.data.message);
    } catch (err) {
      setMessage("Upload failed: " + err.message);
    }
  };

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded shadow-md transition">
      <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Upload File</h2>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4 p-2 border rounded w-full text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700"
      />
      <button
        onClick={handleUpload}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Upload
      </button>
      {message && <p className="mt-2 text-gray-900 dark:text-gray-100">{message}</p>}
    </div>
  );
}
