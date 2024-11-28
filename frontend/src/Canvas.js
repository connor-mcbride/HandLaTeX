import React, { useRef, useState } from 'react';
import axios from 'axios';

const Canvas = () => {
  const svgRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [currentStroke, setCurrentStroke] = useState([]);
  const [strokes, setStrokes] = useState([]);

  const getCoordinates = (e) => {
    const svg = svgRef.current;
    const point = svg.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    const transformedPoint = point.matrixTransform(svg.getScreenCTM().inverse());
    return { x: transformedPoint.x, y: transformedPoint.y };
  };

  const handleMouseDown = (e) => {
    setDrawing(true);
    const coords = getCoordinates(e);
    setCurrentStroke([coords]);
  };

  const handleMouseMove = (e) => {
    if (!drawing) return;
    const coords = getCoordinates(e);
    setCurrentStroke((prev) => [...prev, coords]);
  };

  const handleMouseUp = () => {
    if (!drawing) return;
    setDrawing(false);
    setStrokes((prev) => [...prev, currentStroke]);
    setCurrentStroke([]);
  };

  const handleSend = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/strokes', {
        strokes,
      });
      console.log('Server response:', response.data);
    } catch (error) {
      console.error('Error sending strokes:', error);
    }
  };

  const renderStrokes = () => {
    return strokes.map((stroke, index) => (
      <polyline
        key={index}
        points={stroke.map(point => `${point.x},${point.y}`).join(' ')}
        stroke="black"
        strokeWidth="2"
        fill="none"
      />
    ));
  };

  const renderCurrentStroke = () => {
    if (currentStroke.length === 0) return null;
    return (
      <polyline
        points={currentStroke.map(point => `${point.x},${point.y}`).join(' ')}
        stroke="black"
        strokeWidth="2"
        fill="none"
      />
    );
  };

  return (
    <div>
      <svg
        ref={svgRef}
        width="800"
        height="600"
        style={{ border: '1px solid black' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {renderStrokes()}
        {renderCurrentStroke()}
      </svg>
      <button onClick={handleSend} style={{ marginTop: '10px' }}>
        Send Strokes to Backend
      </button>
    </div>
  );
};

export default Canvas;
