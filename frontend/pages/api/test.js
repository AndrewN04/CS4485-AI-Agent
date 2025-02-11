import axios from 'axios';

export default async function handler(req, res) {
  const response = await axios.get('http://127.0.0.1:5000/api/hello');
  res.status(200).json(response.data);
}
