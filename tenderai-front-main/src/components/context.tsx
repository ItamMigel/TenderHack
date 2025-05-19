"use client";
import { useClientApi } from "@/lib/hooks/useClientApi";
import { handleVoiceText } from "@/lib/voiceText";
import { chatMessagesMock, clustersMock, promptIdeasMock } from "@/mocks";
import { MESSAGE_REVIEW, TChatMessage, TPromptIdea } from "@/types";
import axios from "axios";
import React, { createContext, useContext, useEffect, useState } from "react";

// Create context
const MainContext = createContext({});

// Create a provider component
export const MainContextProvider = ({ children }) => {
    const [dialogueState, setDialogueState] = useState<TChatMessage[]>([]);

    const [prompt, setPrompt] = useState("");

    const [promptIdeasNew, setPromptIdeas] = useState<TPromptIdea[]>(promptIdeasMock);


    const [clusters, setClusters] = useState(clustersMock);

    const [questionId, setQuestionId] = useState<string | null>(null);
    const [feedbackState, setFeedbackState] = useState({
        isOpen: false,
        text: ""
    });

    const [selectedLanguage, setSelectedLanguage] = useState(null);
    const [isChatLoading, setIsLoading] = useState(false);

    const { api } = useClientApi();
    const sendPrompt = async (text = "") => {
        let newText = prompt;
        if (text.length > 0) {
            newText = text;
        }
        const body = { text: newText };


        let clusterId = 0;


        const copy = [...dialogueState];

        copy.push({
            id: Math.random().toString(),
            avatarUrl: "/uploads/users/user.png",
            text: newText,
            isSelf: true,
            isSelected: false,
            review: MESSAGE_REVIEW.none
        });

        setDialogueState(copy);

        setIsLoading(true);
        setPrompt("");

        try {
            const classification = await axios.post("https://hkc7lifxnonzn2-1001.proxy.runpod.net/classify", { text: newText }, { withCredentials: false });
            clusterId = classification.data["class_id"];
        }
        catch (e) {

        }

        if (questionId === null) {
            body.isNew = true;
        }
        else {
            body.isNew = false;
            body["question_id"] = questionId;
        }

        body["cluster_id"] = clusterId + 1;

        console.log(body);


        axios.post("https://hkc7lifxnonzn2-1000.proxy.runpod.net/recommend", { text: newText }).then((res) => {
            const ideas: TPromptIdea[] = [];

            for (const idea of res.data["similar_queries"]) {
                ideas.push({
                    title: idea,
                    description: "",
                    prompt: idea
                });
            }

            setPromptIdeas(ideas);
        });


        api.post("/messages/", body).
            then((res) => {
                console.log(res.data);


                setQuestionId(res.data.answer["question_id"]);


                const answerText = res.data.answer.text;
                copy.push({
                    id: res.data.answer.id,
                    avatarUrl: "/uploads/assistants/1.png",
                    text: res.data.answer.text,
                    isSelf: false,
                    isSelected: false,
                    review: MESSAGE_REVIEW.none
                });


                if (selectedLanguage) {
                    try {
                        handleVoiceText(res.data.answer.text, selectedLanguage).then((res) => {
                            console.log("Yay");
                        }).
                            catch((err) => {
                                console.log(e);
                            });
                    }
                    catch (e) {
                        console.log(e);
                    }
                }
                setDialogueState([...copy]);

                setIsLoading(false);
            }).
            catch((err) => {
                console.error(err);
                setIsLoading(false);
            });
    };
    useEffect(() => {
        console.log("Oh I can do it here!");
    }, []);

    return (
        <MainContext.Provider value = {{
            dialogueState,
            setDialogueState,
            prompt,
            setPrompt,
            clusters,
            setClusters,
            questionId,
            setQuestionId,
            sendPrompt,
            feedbackState,
            setFeedbackState,
            isChatLoading,
            promptIdeasNew,
            setPromptIdeas,
            selectedLanguage,
            setSelectedLanguage
        }}>
            {children}
        </MainContext.Provider>
    );
};

// Custom hook to use the context
export const useMainContext = () => useContext(MainContext);
