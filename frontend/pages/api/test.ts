import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/hello'); // Flask endpoint
    const data = await response.json();

    res.status(200).json(data);
  } catch (error) {
    console.error('Error fetching data from Flask:', error);
    res.status(500).json({ error: 'Failed to fetch data from Flask backend' });
  }
}
