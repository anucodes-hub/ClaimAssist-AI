import { Upload, Database, Loader2 } from 'lucide-react';
import { useState } from 'react';

export default function UploadPage() {
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-dark flex items-center justify-center p-6">
      <div className="max-w-xl w-full bg-surface border border-border rounded-3xl p-10 text-center">
        <h2 className="text-3xl font-bold mb-2">Submit Your Claim</h2>
        <p className="text-gray-500 mb-8">Choose your verification method to proceed</p>

        <div className="grid grid-cols-1 gap-4">
          {/* Main Upload Box */}
          <label className="group border-2 border-dashed border-border hover:border-accent/50 rounded-2xl p-10 cursor-pointer transition flex flex-col items-center">
            <Upload className="text-gray-500 group-hover:text-accent mb-4 transition" size={40} />
            <span className="font-bold">Upload Document</span>
            <span className="text-sm text-gray-500">PDF, JPG or PNG (Max 10MB)</span>
            <input type="file" className="hidden" />
          </label>

          <div className="flex items-center my-4">
            <div className="flex-1 h-px bg-border"></div>
            <span className="px-4 text-xs text-gray-600 uppercase font-bold tracking-widest">or</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>

          {/* DigiLocker Button */}
          <button className="flex items-center justify-center gap-3 bg-white text-black font-bold py-4 rounded-2xl hover:bg-gray-200 transition">
            <Database size={20} /> Import from DigiLocker
          </button>
        </div>

        {loading && (
          <div className="mt-6 flex items-center justify-center gap-2 text-accent">
            <Loader2 className="animate-spin" /> AI Analyzing documents...
          </div>
        )}
      </div>
    </div>
  );
}

/*import { useState } from "react";


export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/api/upload", {
  method: "POST",
  body: formData,
});

const data = await res.json();
setResult(data);
    } catch (error) {
      console.error(error);
      alert("Error uploading document.");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1 className="text-4xl font-bold text-blue-500 mb-6">
        Submit Insurance Claim
      </h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <button
        onClick={handleUpload}
        className="bg-blue-600 px-6 py-3 rounded-lg hover:bg-blue-700"
      >
        Analyze Document
      </button>

      {result && (
        <div className="mt-8 p-6 border border-blue-500 rounded-lg">
          <p className="mb-2">Health Score: {result.health_score}%</p>
          <p className="mb-2">Decision: {result.action}</p>

          {result.flags.length > 0 && (
            <div className="text-red-400 mb-4">
              {result.flags.map((flag, index) => (
                <p key={index}>⚠ {flag}</p>
              ))}
            </div>
          )}

          <pre className="text-gray-400 text-sm">
            {JSON.stringify(result.extracted, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}*/