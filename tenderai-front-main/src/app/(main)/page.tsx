"use client";
import PromptInputWithBottomActions from "@/components/prompt-input-with-bottom-actions";
import React, { useEffect, useState } from "react";
import { Avatar } from "@heroui/react";
import { TAssistant, TChatMessage, TPromptIdea, TPromptIdeaCard } from "@/types";
import ChatMessages from "@/components/chat-messages";
import { assistantsMock, chatMessagesMock, promptIdeasCardsMock, promptIdeasMock } from "@/mocks";
import PromptIdeasCards from "@/components/prompt-ideas-cards";
import { useClientApi } from "@/lib/hooks/useClientApi";
import { useMainContext } from "@/components/context";


export default function HomePage () {
    const [selectedAssistant, setSelectedAssistant] = useState<TAssistant>(assistantsMock[0]);

    const { api } = useClientApi();
    const { dialogueState, setDialogueState } = useMainContext();

    const [promptCardsIdeas, setPromptCardsIdeas] = useState<TPromptIdeaCard[]>([]);

    const [promptIdeas, setPromptIdeas] = useState<TPromptIdea[]>([]);


    useEffect(() => {
        api.get("/general/latest-questions").
            then((res) => {
                let i = 0;

                const newCards: TPromptIdeaCard[] = [];
                for (const promptIdeaCard of Object.keys(res.data.clusters)) {
                    const base = promptIdeasCardsMock[i];
                    i += 1;

                    const ideas: TPromptIdea[] = [];
                    for (const idea of res.data.clusters[promptIdeaCard]) {
                        ideas.push({
                            title: idea,
                            description: "",
                            prompt: idea
                        });
                    }
                    base.ideas = ideas;

                    newCards.push(base);
                }
                const newIdeas: TPromptIdea[] = [];
                for (const idea of res.data.latest) {
                    newIdeas.push({
                        title: idea,
                        prompt: idea,
                        description: ""
                    });
                }
                setPromptIdeas(newIdeas);
                console.log(newCards);
                setPromptCardsIdeas(newCards);
            }).
            catch((err) => {
                console.error(err);
            });
    }, []);
    return (
        <div className = "h-full overflow-y-auto pb-4 pt-8">
            {dialogueState.length === 0 &&
            <div className = "flex flex-col justify-center gap-10">
                <div className = "flex w-full flex-col items-center justify-center gap-2">
                    <Avatar
                        size = "lg"
                        src = "https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
                    />
                    <h1 className = "text-xl font-medium text-default-700">Как я могу Вам помочь?</h1>
                </div>
                <div className = "w-full">
                    <div className = "mx-auto w-[806px]">
                        <PromptIdeasCards promptIdeasCards = {promptCardsIdeas} />
                    </div>

                </div>
            </div>
            }
            {dialogueState.length > 0 &&
            <div>
                <div className = "flex h-[60px] items-center gap-x-4 pb-6">
                    <img src = {selectedAssistant.avatarUrl} className = "size-10"/>
                    <div>
                        <div className = "text-[30px] font-bold leading-[36px]">{selectedAssistant.title}</div>
                        <div className = "text-[16px] leading-[24px]">Бот ассистент</div>
                    </div>
                </div>
                <div className = "h-[374px]">
                    <ChatMessages messages = {dialogueState} isReviewClickable = {true}/>
                </div>
            </div>
            }
            <div className = "mt-8 flex flex-col gap-2">
                <PromptInputWithBottomActions promptIdeas = {promptIdeas}/>
                <p className = "px-2 text-tiny text-default-400">
                    Искусственный интеллект иногда ошибается, будьте внимательный.
                </p>
            </div>
        </div>
    );
}
