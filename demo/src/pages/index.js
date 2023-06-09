import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

const API_KEY = 'redacted';

const Home = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [jobId, setJobId] = useState('');
  const [processing, setProcessing] = useState(false);
  const [answer, setAnswer] = useState('');
  const [pollcount, setPollcount] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);

    const response = await axios.post(
      'https://mango.sievedata.com/v1/push',
      {
        workflow_name: 'video_qa',
        inputs: {
          video: {
            url: videoUrl,
          },
          question,
          namespace: uuidv4(),
        },
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
        },
      }
    );

    setJobId(response.data.id);
    checkJobStatus(response.data.id);
    setPollcount(0);
  };

  const checkJobStatus = async (jobId) => {
    const intervalId = setInterval(async () => {
      const response = await axios.get(
        `https://mango.sievedata.com/v1/jobs/${jobId}`,
        {
          headers: {
            'X-API-Key': 'redacted',
          },
        }
      );

      if (response.data.status === 'finished') {
        clearInterval(intervalId);
        setProcessing(false);
        const parsedData = JSON.parse(response.data.data[0]);
        console.log(parsedData);
        setVideoUrl(parsedData.video);
        setAnswer(parsedData.gpt_output);
      } else {
        console.log('Job is still processing...');
        setPollcount((prevCount) => prevCount + 1);
      }
    }, 1000); // Poll every 1 seconds
  };

  return (
    <div className="min-h-screen bg-indigo-500 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-6">Video QA</h1>
        </div>
        <div className="p-8 bg-white rounded-xl shadow-md">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-extrabold text-gray-900">Submit a video and question</h2>
            </div>
            <input
              type="text"
              placeholder="Video URL"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              type="text"
              placeholder="Question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div className="flex justify-center">
              <button
                type="submit"
                className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Submit
              </button>
            </div>
          </form>
          {jobId && (
            <div className="text-center">
              <p className="mt-4 text-xl">Job ID: {jobId}</p>
            </div>
          )}
          {processing && (
            <div className="text-center">
              <p className="mt-4 text-xl text-indigo-600 font-bold">Processing... ({pollcount}s)</p>
            </div>
          )}
        </div>

        {videoUrl && (
          <div className="mt-8 p-8 bg-white rounded-xl shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Video:</h2>
            <video
              src={videoUrl}
              controls
              className="w-full max-w-lg rounded-md shadow-lg"
            ></video>
          </div>
        )}

        {answer && (
          <div className="mt-8 p-8 bg-white rounded-xl shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Answer:</h2>
            <p className="text-xl">{answer}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;