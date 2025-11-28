import { useState } from "react";
import { FaChevronRight } from "react-icons/fa";

export default function JsonCard({ item, type }) {
  const [expanded, setExpanded] = useState(false);

  const hasChildren = type === "epic" ? item.stories?.length : type === "story" ? item.qa?.length : false;

  return (
    <div className="border rounded shadow p-4 mb-2 cursor-pointer bg-white dark:bg-gray-800 transition-all duration-300">
      <div className="flex items-center justify-between" onClick={() => setExpanded(!expanded)}>
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">{item.title || item.question}</h3>
        {hasChildren && <FaChevronRight className={`transition-transform duration-300 ${expanded ? "rotate-90" : ""}`} />}
      </div>

      {expanded && hasChildren && (
        <div className="mt-2 ml-6 space-y-2">
          {type === "epic" &&
            item.stories.map((story) => <JsonCard key={story.id} item={story} type="story" />)}
          {type === "story" &&
            item.qa.map((qa) => <JsonCard key={qa.id} item={qa} type="qa" />)}
        </div>
      )}

      {expanded && type === "qa" && (
        <p className="mt-1 ml-6 text-gray-700 dark:text-gray-300">{item.answer}</p>
      )}
    </div>
  );
}
