import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { Clock, Pause, Play, RotateCcw, ArrowRight, Table } from 'lucide-react';

const BOX_SIZE = 90;
const EMOJI_SIZE = 40;

export default function App() {
  const [gameState, setGameState] = useState({
    beast: null,
    engineers: [],
    walls: [],
    game_over: false,
    zombie_order: [],
    beast_hidden: true,
    turn_counter: 0,
    grid_size: [],
    current_turn_entity: '',
    beast_target: null,
    csv_results: [],
    end_game_turns: '?'
  });

  const [elapsedTime, setElapsedTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const GRID_WIDTH = gameState.grid_size[0];
  const GRID_HEIGHT = gameState.grid_size[1];

  const [showResults, setShowResults] = useState(false);

  const fetchGameState = useCallback(async () => {
    if (isPaused) return;
    try {
      const response = await fetch('http://localhost:5000/update');
      const data = await response.json();
      if (data.update_occurred) {
        setGameState(data);
        setElapsedTime(prevTime => prevTime + 1);

        if (data.game_over) {
          setIsPaused(true);
        }
      }
    } catch (error) {
      console.error('Error fetching game state:', error);
    }
  }, [isPaused]);

  useEffect(() => {
    const intervalId = setInterval(fetchGameState, 500);  // Poll more frequently
    return () => clearInterval(intervalId);
  }, [fetchGameState]);


  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePauseResume = () => {
    setIsPaused(prev => !prev);
  };

  const handleReset = async () => {
    try {
      const response = await fetch('http://localhost:5000/reset', { method: 'POST' });
      const data = await response.json();
      setGameState(data);
      setElapsedTime(0);
      setIsPaused(false);
    } catch (error) {
      console.error('Error resetting game:', error);
    }
  };

  const handleToggleResults = () => {
    setShowResults(prev => !prev);
  };
  const calculateTotal = (player) => {
    return Object.keys(player)
      .filter(key => key.startsWith('Game'))
      .reduce((total, key) => {
        const score = parseInt(player[key]);
        return isNaN(score) ? total : total + score;
      }, 0);
  };

  const getCellStyle = (x, y) => {
    const baseStyle = {
      width: BOX_SIZE,
      height: BOX_SIZE,
      backgroundColor: '#4A5568',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      fontSize: `${EMOJI_SIZE}px`,
      border: '1px solid #2D3748',
      boxSizing: 'border-box',
      position: 'relative',
    };
  
    const engineer = gameState.engineers.find(
      (eng) => eng.position[0] === x && eng.position[1] === y
    );
    if (engineer) {
      if (gameState.beast_target['Beast'] === engineer.name && !gameState.beast_hidden) {
        baseStyle.border = '3px solid red';
      } else {
        const zombieTargets = Object.entries(gameState.beast_target)
          .filter(([key, value]) => key !== 'Beast' && value === engineer.name);
        if (zombieTargets.length > 0) {
          baseStyle.border = '3px solid blue';
        }
      }
    }
  
    return baseStyle;
  };

  return (
    <div className="flex flex-col ">
      <div className="flex bg-gray-900 text-white p-4 w-full justify-center">
        <div 
          className="game-header flex justify-between items-center"
          style={{ maxWidth: `${GRID_WIDTH * BOX_SIZE}px` }}
        >
          <h1 className="text-4xl font-bold">The Beast from 3 East</h1>
          <div 
            className="game-controls flex justify-between items-center mt-4"
            style={{ maxWidth: `${GRID_WIDTH * BOX_SIZE}px` }}
          >
            <button 
              onClick={handlePauseResume}
              className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition-colors"
            >
              {isPaused ? <Play size={24} /> : <Pause size={24} />}
            </button>
            <button 
              onClick={handleReset}
              className="p-2 bg-red-500 rounded hover:bg-red-600 transition-colors"
            >
              <RotateCcw size={24} />
            </button>
            <button 
              onClick={handleToggleResults}
              className="p-2 bg-green-500 rounded hover:bg-green-600 transition-colors"
            >
              <Table size={24} />
            </button>
          </div>
          <div className="game-clock justify-center flex items-center">
            <span className="text-xl">Turn: {gameState.turn_counter}/{gameState.end_game_turns}</span>
          </div>
          
        </div>
        
      </div>
      <div 
          className="game-header flex justify-between items-center"
          style={{ maxWidth: `${GRID_WIDTH * BOX_SIZE}px` }}
        >

    {gameState.game_over && (
      <div className="flex flex-col items-center min-h-screen bg-gray-300 text-white p-8">
            <h2 className="text-2xl font-bold">Game Over!</h2>
          </div>
        )}
        
      {gameState.turn_counter >= 10 && gameState.turn_counter <= 13 && (
      <div className="flex flex-col items-center bg-gray-300 text-white p-4">
            <h2 className="text-2xl font-bold">LEEERROOOOYY!!!</h2>
          </div>
        )}
      </div>
        

      
      <div className="game-content relative">
        <div className="game-board-container flex-grow">
          <div
            className="game-board"
            style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${GRID_WIDTH}, ${BOX_SIZE}px)`,
              gridTemplateRows: `repeat(${GRID_HEIGHT}, ${BOX_SIZE}px)`,
              gap: '1px',
              padding: '10px',
              backgroundColor: '#2D3748',
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
          >
            {Array.from({ length: GRID_WIDTH * GRID_HEIGHT }).map((_, index) => {
              const x = index % GRID_WIDTH;
              const y = Math.floor(index / GRID_WIDTH);
              let content = '';
              let initials = '';

              if (!gameState.beast_hidden && gameState.beast && gameState.beast[0] === x && gameState.beast[1] === y) {
                content = '👹';
                initials = 'Beast';
              } else {
                const engineer = gameState.engineers.find(
                  (eng) => eng.position[0] === x && eng.position[1] === y
                );
                if (engineer) {
                  content = engineer.emoji;
                  initials = engineer.name;
                }
              }

              return (
                <div
                  key={index}
                  style={getCellStyle(x, y)}
                >
                  <span>{content}</span>
                  <span style={{ fontSize: '12px', position: 'absolute', bottom: '2px' }}>{initials}</span>
                </div>
              );
            })}
          </div>
        </div>
        
      {/* New Turn Order Table */}
      <div className="turn-order-table mt-4 p-4 bg-gray-800 rounded" style={{ maxWidth: `${GRID_WIDTH * BOX_SIZE}px` }}>
        <h2 className="text-xl font-bold mb-2 text-white">Turn Order</h2>
        <table className="w-full">
          <tbody>
            <tr>
              <td>{gameState.current_turn_entity === 'Beast' && <ArrowRight size={24} />}</td>
              <td>👹</td>
              <td>Beast</td>
            </tr>
            {gameState.engineers.map((engineer, index) => (
              <tr key={index}>
                <td>{gameState.current_turn_entity === engineer.name && <ArrowRight size={24} />}</td>
                <td>{engineer.emoji}</td>
                <td>{engineer.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      </div>



{showResults && gameState.csv_results.length > 0 && (
  <div className="results-table mt-4 p-4 bg-gray-800 rounded" 
       style={{ width: `${GRID_WIDTH * BOX_SIZE}px`, margin: 'auto' }}>
    <h2 className="text-xl font-bold mb-2 text-white">Game Results</h2>
    <div className="overflow-x-auto">
      <table className="game-results-table w-full border-collapse">
        <thead>
          <tr>
            <th className="results-cell">Name</th>
            {Object.keys(gameState.csv_results[0]).filter(key => key.startsWith('Game')).map(gameKey => (
              <th key={gameKey} className="results-cell">{gameKey}</th>
            ))}
            <th className="results-cell">Total</th>
          </tr>
        </thead>
        <tbody>
          {gameState.csv_results.map((player, index) => (
            <tr key={index}>
              <td className="results-cell">{player.Name}</td>
              {Object.keys(player).filter(key => key.startsWith('Game')).map(gameKey => (
                <td key={gameKey} className="results-cell results-cell-number">{player[gameKey] || '-'}</td>
              ))}
              <td className="results-cell results-cell-number">{calculateTotal(player)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
)}
    </div>
  );
}
