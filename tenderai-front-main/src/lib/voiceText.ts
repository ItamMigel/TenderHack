export const handleVoiceText = async (text: string, language: string) => {
    try {
        const response = await fetch("http://localhost:8000/api/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                language: language
            })
        });
        if (!response.ok) {
            throw new Error("Ошибка озвучивания текста");
        }
        // Получаем аудиоданные в виде blob
        const blob = await response.blob();
        // Создаём URL для воспроизведения аудио
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.play();
    }
    catch (err) {
        console.error(err);
    }
};
