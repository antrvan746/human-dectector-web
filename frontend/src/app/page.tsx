"use client";

import { useState, useCallback } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, X, Image as ImageIcon } from "lucide-react";

interface DetectionMetadata {
  author_name: string;
  author_email?: string;
  title?: string;
  description?: string;
}

interface Detection {
  id: number;
  original_image_path: string;
  visualized_image_path?: string;
  number_of_persons: number;
  author_name: string;
  title?: string;
  status: string;
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [progress, setProgress] = useState(0);
  const [userData, setUserData] = useState({
    authorName: "",
    authorEmail: "",
    description: "",
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".gif"],
    },
    multiple: true,
  });

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError("Please select at least one file");
      return;
    }

    if (!userData.authorName) {
      setError("Please enter your name");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append("file", file);

        const metadata: DetectionMetadata = {
          author_name: userData.authorName,
          author_email: userData.authorEmail || undefined,
          title: file.name,
          description: userData.description || undefined,
        };

        Object.keys(metadata).forEach((key) => {
          formData.append(key, metadata[key as keyof DetectionMetadata] || "");
        });

        const response = await axios.post(
          "http://localhost:8000/api/detect",
          formData
        );
        setDetections((prev) => [...prev, response.data]);
        setProgress(((i + 1) / files.length) * 100);
      }
      setFiles([]);
      setProgress(0);
    } catch (err) {
      setError("Error processing images. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-medium">
              Human Detection
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* User Form */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="authorName">Name *</Label>
                <Input
                  id="authorName"
                  placeholder="Enter your name"
                  value={userData.authorName}
                  onChange={(e) =>
                    setUserData((prev) => ({
                      ...prev,
                      authorName: e.target.value,
                    }))
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="authorEmail">Email</Label>
                <Input
                  id="authorEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={userData.authorEmail}
                  onChange={(e) =>
                    setUserData((prev) => ({
                      ...prev,
                      authorEmail: e.target.value,
                    }))
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  placeholder="Add a description"
                  value={userData.description}
                  onChange={(e) =>
                    setUserData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            {/* Compact Drop Zone */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-4 transition-colors duration-200 cursor-pointer
                ${
                  isDragActive
                    ? "border-primary bg-primary/5"
                    : "border-gray-200 hover:border-primary"
                }`}
            >
              <input {...getInputProps()} />
              <div className="flex flex-col items-center gap-2">
                <Upload className="h-6 w-6 text-gray-400" />
                <p className="text-sm text-gray-600 text-center">
                  {isDragActive ? "Drop here" : "Drop images or click"}
                </p>
              </div>
            </div>

            {/* Compact File List */}
            {files.length > 0 && (
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between py-1 px-2 bg-gray-50 rounded-md text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <ImageIcon className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600 truncate max-w-[180px]">
                        {file.name}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => removeFile(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Progress Bar */}
            {loading && <Progress value={progress} className="h-1" />}

            {/* Submit Button */}
            <Button
              className="w-full"
              onClick={handleSubmit}
              disabled={loading || files.length === 0}
            >
              {loading ? "Processing..." : "Upload and Detect"}
            </Button>

            {/* Error Message */}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </CardContent>
        </Card>

        {/* Results Card */}
        {detections.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {detections.map((detection) => (
                <div
                  key={detection.id}
                  className="flex justify-between items-center p-2 bg-gray-50 rounded-md"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{detection.title}</p>
                    <p className="text-xs text-gray-500">
                      Persons detected: {detection.number_of_persons}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      detection.status === "completed"
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {detection.status}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}