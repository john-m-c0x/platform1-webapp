export interface TrainDeparture {
  live_time?: string;
  disruption_dated?: string;
  updating?: boolean;
  scheduled_time?: string;
  estimated_time?: string;
  platform?: string;
  destination?: string;
  created_at?: string;
  id?: string;
  disruptions?: any[];
}

interface ApiResponse {
  departures: TrainDeparture[];
}

const API_URL = process.env.REACT_APP_API_GATEWAY_URL || '';

export const fetchTrainDepartures = async (): Promise<TrainDeparture[]> => {
  try {
    console.log('Fetching train departures from:', API_URL);
    const response = await fetch(API_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      mode: 'cors' // Enable CORS
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error Response:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const responseData = await response.json();
    console.log('API Response data:', responseData);

    // The API might return data in different structures
    // Case 1: Direct object with departures array
    if (responseData && responseData.departures && Array.isArray(responseData.departures)) {
      return responseData.departures;
    }
    
    // Case 2: Stringified JSON in the body property
    if (responseData && responseData.body && typeof responseData.body === 'string') {
      try {
        const parsedBody = JSON.parse(responseData.body);
        console.log('Parsed body:', parsedBody);
        
        if (parsedBody && parsedBody.departures && Array.isArray(parsedBody.departures)) {
          return parsedBody.departures;
        }
      } catch (e) {
        console.error('Error parsing body JSON:', e);
      }
    }
    
    // Case 3: Body is already an object
    if (responseData && responseData.body && responseData.body.departures && Array.isArray(responseData.body.departures)) {
      return responseData.body.departures;
    }

    console.error('Invalid data format:', responseData);
    throw new Error('Invalid data format received');
  } catch (error) {
    console.error('Error fetching train departures:', error);
    throw error;
  }
}; 