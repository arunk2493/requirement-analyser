import { useEffect, useState } from "react";
import JsonCard from "./JsonCard";
import { fetchQA } from "../api/api";

export default function QAPage() {
  const [qa, setQA] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQA().then(setQA).finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (!qa.length) return <p>No QA found.</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">QA</h2>
      {qa.map((q) => (
        <JsonCard key={q.id} item={q} type="qa" />
      ))}
    </div>
  );
}
