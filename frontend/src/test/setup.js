import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Real localStorage implementation for testing
const localStorageData = {};
const localStorageMock = {
  getItem: (key) => localStorageData[key] ?? null,
  setItem: (key, value) => {
    localStorageData[key] = String(value);
  },
  removeItem: (key) => {
    delete localStorageData[key];
  },
  clear: () => {
    Object.keys(localStorageData).forEach(key => delete localStorageData[key]);
  },
  get length() {
    return Object.keys(localStorageData).length;
  },
  key: (index) => Object.keys(localStorageData)[index] ?? null,
};
Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

