"use client";

import { useState, ChangeEvent } from "react";

function debounce(func: Function, wait: number) {
  let timeout: NodeJS.Timeout;

  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export default function Home() {
  const [inputJSON, setInputJSON] = useState("");
  const [outputJSON, setOutputJSON] = useState("");

  async function convertSwagger(currentInputJSON: string) {
    try {
      const response = await fetch("https://api.swaggerconverter.com/convert", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: currentInputJSON,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  }

  const handleConvert = async (currentInputJSON: string) => {
    const convertedJSON = await convertSwagger(currentInputJSON);
    if (convertedJSON) {
      setOutputJSON(convertedJSON);
    }
  };

  // Apply debounce to the handleConvert function
  const debouncedHandleConvert = debounce(
    (currentInputJSON: string) => handleConvert(currentInputJSON),
    1000
  );

  const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const currentInputValue = e.target.value;
    setInputJSON(currentInputValue);
    debouncedHandleConvert(currentInputValue);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow p-4">
        <div className="font-medium text-xl text-gray-700">
          Swagger Converter
        </div>
      </div>

      {/* Body */}
      <div className="flex-grow flex p-4 space-x-4">
        {/* Left Side */}
        <div className="flex-grow flex flex-col">
          <label className="mb-2 text-gray-700">Input (Swagger 2.0 JSON)</label>
          <textarea
            className="flex-grow p-4 bg-white border-2 border-gray-300 rounded-lg shadow-md focus:ring focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Enter JSON here..."
            value={inputJSON}
            onChange={handleInputChange}
          />
        </div>

        {/* Right Side */}
        <div className="flex-grow flex flex-col">
          <label className="mb-2 text-gray-700">
            Output (Swagger 3.0 JSON)
          </label>
          <textarea
            className="flex-grow p-4 bg-white border-2 border-gray-300 rounded-lg shadow-md focus:ring focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Converted JSON will appear here..."
            value={outputJSON}
            readOnly
          />
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 bg-white shadow-md flex justify-between items-center">
        <div className="text-gray-700">
          Created by{" "}
          <a
            href="https://jedpatterson.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 hover:underline"
          >
            Jed Patterson
          </a>
        </div>
      </div>
    </div>
  );
}
