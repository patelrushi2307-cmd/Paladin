import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/global.css';
import './styles/detectors.css';
import './styles/pages.css';
import { App } from './app/App';

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
