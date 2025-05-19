import { SubtitleSettings, defaultSettings } from "./SubtitleSettings";
import React, { FC, useRef, useState, useEffect } from "react";
import { Card, CardBody, Button } from "@heroui/react";
import { SupportedLanguage } from "@/types/language";


interface VideoStreamProps {
  language: SupportedLanguage;
  onSubtitleChange: (data: { time: string; text: string }) => void;
  onSummaryChange: (data: { time: string; text: string }) => void;
  onPermissionGranted?: () => void;
  onPermissionDenied?: () => void;
  onTranscription?: (data: any) => void;
}

export const VideoStream: FC<VideoStreamProps> = ({
    language,
    onSubtitleChange,
    onPermissionGranted,
    onPermissionDenied,
}) => {
    const [status, setStatus] = useState<"idle" | "waiting" | "streaming" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState<string>("");
    const [currentSubtitle, setCurrentSubtitle] = useState<string>("");
    const [debugInfo, setDebugInfo] = useState<string>("Starting...");
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const [subtitleSettings] = useState<SubtitleSettings>(defaultSettings);

    const startStream = async () => {
        setStatus("waiting");
        setErrorMessage("");
        setDebugInfo("Starting stream...");

        try {
            // Сначала получаем стрим
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: {
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                }
            });

            streamRef.current = stream;
            if (videoRef.current) videoRef.current.srcObject = stream;

            // Получаем актуальный sample rate из трека
            const audioTrack = stream.getAudioTracks()[0];
            const settings = audioTrack.getSettings();
            const actualSampleRate = settings.sampleRate || 48000; // Обычно браузеры используют 48кГц

            setDebugInfo((prev) => prev + `\nAudio track settings: ${JSON.stringify(settings)}`);

            // Создаем AudioContext с правильным sample rate
            const audioContext = new AudioContext({ sampleRate: actualSampleRate });
            audioContextRef.current = audioContext;

            const source = audioContext.createMediaStreamSource(stream);
            const processor = audioContext.createScriptProcessor(1024, 1, 1);

            // Создаем WebSocket соединение
            const ws = new WebSocket("ws://localhost:8000/ws");
            wsRef.current = ws;

            source.connect(processor);
            processor.connect(audioContext.destination);

            processor.onaudioprocess = (e) => {
                if (ws.readyState === WebSocket.OPEN) {
                    const inputData = e.inputBuffer.getChannelData(0);

                    // Увеличим громкость
                    const amplifiedData = new Float32Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {
                        // Усиливаем сигнал в 2 раза
                        amplifiedData[i] = Math.max(-1, Math.min(1, inputData[i] * 2));
                    }

                    // Конвертируем в Int16
                    const intData = new Int16Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {
                        intData[i] = Math.max(-32768, Math.min(32767, amplifiedData[i] * 32768));
                    }

                    // Добавим логирование
                    const maxAmplitude = Math.max(...Array.from(intData).map(Math.abs));
                    console.log("Sending audio chunk:", {
                        length: intData.length,
                        maxAmplitude: maxAmplitude
                    });

                    ws.send(intData.buffer);
                }
            };

            ws.onmessage = (event) => {
                const text = event.data;
                setCurrentSubtitle(text);
                const time = new Date().toLocaleTimeString();
                onSubtitleChange({
                    time,
                    text
                });
                setDebugInfo((prev) => prev + "\nReceived subtitle: " + text);
            };

            ws.onopen = () => {
                setStatus("streaming");
                onPermissionGranted && onPermissionGranted();
                setDebugInfo((prev) => prev + "\nWebSocket connected");
            };

            ws.onerror = (error) => {
                setDebugInfo((prev) => prev + "\nWebSocket error: " + error);
                setStatus("error");
                setErrorMessage("Ошибка подключения к серверу");
            };

            ws.onclose = () => {
                setDebugInfo((prev) => prev + "\nWebSocket closed");
                if (status === "streaming") {
                    setStatus("error");
                    setErrorMessage("Соединение прервано");
                }
            };
        }
        catch (err) {
            setDebugInfo((prev) => prev + "\nStream error: " + String(err));
            let message = "Ошибка доступа к камере";
            if (err instanceof Error) {
                if (err.name === "NotAllowedError") message = "Доступ к камере запрещён";
                else if (err.name === "NotFoundError") message = "Камера не найдена";
                else if (err.name === "NotReadableError") message = "Камера уже используется другим приложением";
            }
            setErrorMessage(message);
            setStatus("error");
            onPermissionDenied && onPermissionDenied();
        }
    };

    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach((track) => track.stop());
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, []);

    return (
        <div>{status === "streaming" && currentSubtitle}</div>
    );
};
