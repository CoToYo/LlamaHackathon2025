import { NextRequest } from 'next/server';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { writeFile } from 'fs/promises';
import { join } from 'path';

const s3Client = new S3Client({
  region: 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return new Response('No file uploaded', { status: 400 });
    }

    // Save locally
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const localPath = join(process.cwd(), 'temp.txt');
    await writeFile(localPath, buffer);

    // Upload to S3
    const command = new PutObjectCommand({
      Bucket: process.env.AWS_BUCKET_NAME,
      Key: 'seller_input.txt',
      Body: buffer,
      ContentType: 'text/plain',
    });

    await s3Client.send(command);

    return new Response('File uploaded successfully', { status: 200 });
  } catch (error) {
    console.error('Error uploading file:', error);
    return new Response('Error uploading file', { status: 500 });
  }
} 