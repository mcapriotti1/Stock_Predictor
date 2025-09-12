'use client';
import { ChangeEvent } from 'react';

interface SearchBarProps {
  value: string;
  onChange: (val: string) => void;
}

export default function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e: ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
      placeholder="Search ticker..."
      style={{ fontSize: 20, width: '100%', padding: '0.5rem', marginTop: "1rem", marginBottom: '1rem', color: 'white', backgroundColor: "black", outline: "none"}}
    />
  );
}
