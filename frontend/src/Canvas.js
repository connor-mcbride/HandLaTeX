import React, { useRef, useState } from 'react';
import axios from 'axios';
import './Canvas.css';

const Canvas = () => {
  const svgRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [currentStroke, setCurrentStroke] = useState([]);
  const [strokes, setStrokes] = useState([]);

  /**
   * Extracts SVG coordinates from a Pointer Event.
   * @param {PointerEvent} e - The pointer event. 
   * @returns - Th ex, y coordinates and a timestamp
   */
  const getCoordinates = (e) => {
    const svg = svgRef.current;
    const point = svg.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    const transformedPoint = point.matrixTransform(svg.getScreenCTM().inverse());
    return { x: transformedPoint.x, y: transformedPoint.y, t: Date.now() };
  };

  /**
   * Handles the start of a pointer interaction.
   * @param {PointerEvent} e - The pointer down event.
   */
  const handlePointerDown = (e) => {
    e.preventDefault();
    setDrawing(true);
    const coords = getCoordinates(e);
    setCurrentStroke([coords]);

    // Continue receiving points even if it leaves the SVG
    if (svgRef.current) {
      svgRef.current.setPointerCapture(e.pointerId);
    }
  };

  /**
   * Handles the movement of a pointer.
   * @param {PointerEvent} e - The pointer move event.
   */
  const handlePointerMove = (e) => {
    e.preventDefault();
    if (!drawing) return;
    const coords = getCoordinates(e);
    setCurrentStroke((prev) => [...prev, coords]);
  };

  /**
   * Handles the end of a pointer interaction.
   * @param {PointerEvent} e - The pointer up or leave event.
   */
  const handlePointerUp = (e) => {
    e.preventDefault();
    if (!drawing) return;
    setDrawing(false);
    setStrokes((prev) => [...prev, currentStroke]);
    setCurrentStroke([]);

    // Release the pointer
    if (svgRef.current) {
      svgRef.current.releasePointerCapture(e.pointerId);
    }
  };

  /**
   * Renders all completed strokes.
   * @returns {JSX.Element[]} - An array of polyline elements.
   */
  const renderStrokes = () => {
    return strokes.map((stroke, index) => (
      <polyline
        key={index}
        points={stroke.map(point => `${point.x},${point.y}`).join(' ')}
        stroke="black"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ));
  };

  /**
   * Renders the stroke currently being drawn.
   * @returns {JSX.Element|null} - A polyline element or null.
   */
  const renderCurrentStroke = () => {
    if (currentStroke.length === 0) return null;
    return (
      <polyline
        points={currentStroke.map(point => `${point.x},${point.y}`).join(' ')}
        stroke="black"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    );
  };

  /**
   * Sends the collected strokes data to the backend.
   */
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

  /**
   * Clears all strokes from the canvas.
   */
  const handleClear = () => {
    setStrokes([]);
    setCurrentStroke([]);
  }

  return (
    <div>
      <svg
        ref={svgRef}
        viewBox="0 0 800 600"
        className="drawing-canvas"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      >
        {renderStrokes()}
        {renderCurrentStroke()}
      </svg>
      <div style={{ marginTop: '10px' }}>
        <button onClick={handleSend} style={{ marginRight: '10px' }}>
          Send Strokes to Backend
        </button>
        <button onClick={handleClear}>
          Clear Canvas
        </button>
      </div>
    </div>
  );
};

export default Canvas;
