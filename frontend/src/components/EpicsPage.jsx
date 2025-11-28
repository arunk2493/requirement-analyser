import { useEffect, useState } from "react";
import JsonCard from "./JsonCard.jsx";
import { fetchEpics } from "../api/api";

export default function EpicsPage() {
  const [epics, setEpics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEpics().then(setEpics).finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (!epics.length) return <p>No epics found.</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Epics</h2>
      {epics.map((epic) => (
        <JsonCard key={epic.id} item={epic} type="epic" />
      ))}
    </div>
  );
}
