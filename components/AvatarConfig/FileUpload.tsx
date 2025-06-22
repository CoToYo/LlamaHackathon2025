import React, { useRef } from 'react';
import { Field } from './Field';
import { Button } from '../Button';

export const FileUpload: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload-script', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file');
    }
  };

  return (
    <Field label="Upload Script">
      <div className="flex flex-row gap-2">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".txt"
          className="hidden"
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          className="w-full"
        >
          Choose File
        </Button>
      </div>
    </Field>
  );
}; 