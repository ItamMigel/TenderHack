"use client";

import { useMainContext } from "./context";
import type { CardProps } from "@heroui/react";

import React from "react";
import { Button, Card, CardBody, CardHeader } from "@heroui/react";
import { Icon } from "@iconify/react";
import { TPromptIdea, TPromptIdeaCard } from "@/types";


export type PromptIdeaCardProps = {card: TPromptIdeaCard};

const PromptIdeaCard = React.forwardRef<HTMLDivElement, PromptIdeaCardProps>((props, ref) => {
    const { card } = props;

    const { dialogueState, setDialogueState, prompt, setPrompt } = useMainContext();

    const handleButtonPress = (text) => {
        setPrompt(text);
    };

    return (
        <Card ref = {ref} className = "bg-primary" shadow = "none" {...props}>
            <CardHeader className = "flex flex-col gap-2 px-4 pb-4 pt-6">
                <Icon icon = {card.iconUrl} width = {40}/>
                <p className = "text-medium text-content2-foreground">{card.title}</p>
            </CardHeader>
            <CardBody className = "flex flex-col gap-2">
                {card.ideas.map((promptIdea, index) => <Button
                    onPress = {() => { handleButtonPress(promptIdea.title); }}
                    key = {index}
                    className = "max-h-max min-h-[50px] !whitespace-normal rounded-medium bg-primary-dark px-3 py-2 text-content3-foreground"
                >
                    {promptIdea.title}
                </Button>)}
            </CardBody>
        </Card>
    );
},);

PromptIdeaCard.displayName = "PromptIdeaCard";

export default PromptIdeaCard;
