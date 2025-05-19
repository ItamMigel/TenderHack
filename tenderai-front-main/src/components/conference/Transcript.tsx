import { FC } from 'react';
import { Card, CardBody, CardHeader, Button } from "@heroui/react";

interface TranscriptEntry {
  id: string;
  speaker: string;
  time: string;
  text: string;
}

interface TranscriptProps {
  entries: TranscriptEntry[];
}

export const Transcript: FC<TranscriptProps> = ({ entries }) => {
  return (
    <Card>
      <CardHeader className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Транскрипция</h3>
        <Button color="primary">
          Краткое содержание
        </Button>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          {entries.map((entry) => (
            <div key={entry.id} className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-200 rounded-full flex items-center justify-center">
                {entry.speaker}
              </div>
              <div>
                <div className="text-sm text-gray-500">{entry.time}</div>
                <div>{entry.text}</div>
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
};