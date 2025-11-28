import { useEffect, useState } from "react";
import JsonCard from "./JsonCard.jsx";
import { fetchStories } from "../api/api";

export default function StoriesPage() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStories().then(setStories).finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (!stories.length) return <p>No stories found.</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Stories</h2>
      {stories.map((story) => (
        <JsonCard key={story.id} item={story} type="story" />
      ))}
    </div>
  );
}
