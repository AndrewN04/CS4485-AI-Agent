import { useState, useEffect } from "react";

const Home: React.FC = () => {
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await fetch("/api/hello");
        const data = await response.json();
        setMessage(data.message);
      } catch (error) {
        console.error("Error fetching data:", error);
        setMessage("Failed to fetch message from Flask backend.");
      }
    };

    fetchMessage();
  }, []);

  return (
    <div>
      <h1>{message ? message : "Loading..."}</h1>
    </div>
  );
};

export default Home;
