import PromptIdeaCard from "./prompt-idea-card";
import React from "react";
import { Icon } from "@iconify/react";
import { TPromptIdeaCard } from "@/types";


export type PromptIdeasCardsProps = {promptIdeasCards: TPromptIdeaCard[]};

export default function PromptIdeasCards (props: PromptIdeasCardsProps) {
    const { promptIdeasCards } = props;

    return (
        <div className = "grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
            {promptIdeasCards.map((card) => <PromptIdeaCard
                key = {card.id}
                card = {card}
            />)}
        </div>
    );
}
