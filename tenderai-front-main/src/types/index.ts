

export enum MESSAGE_REVIEW {
    "none" = 0,
    "like" = 1,
    "dislike" = 2,
}



export type TPromptIdea = {
    title: string;
    description: string;
    prompt: string;
}
export type TChatMessage = {
    id: string;
    avatarUrl: string;
    text: string;
    isSelf: boolean;
    isSelected: boolean;
    review: MESSAGE_REVIEW
}


export type TAssistantSettings = {
    temperature: number;
    maxLength: number;
    topP: number;
    frequencyPenalty: number;
    presencePenalty: number;
}

export type TDataset = {
    id: string;
    title: string;
}
export type TAssistant = {
    id: string;
    title: string;
    avatarUrl: string;
    neuralNetworkTitle: string;
    gradient: string;
    settings: TAssistantSettings;
    dataset: TDataset;
};


export type TDialogue = {
    id: string;
    assistant: TAssistant;
    messages: TChatMessage[];
}

export type TQuestionCluster = {
    id: string;
    color: string;
    title: string;
}

export type TQuestion = {
    id: string;
    assistant: TAssistant;
    dialogue: TChatMessage[];
    askedAt: number;
    cluster: TQuestionCluster;
}

export type TPromptIdeaCard = {
    id: string;
    title: string;
    iconUrl: string;
    ideas: TPromptIdea[]
}

export type TStatsChip = {
    title: string;
    value: string;
    change: string;
    changeType: "positive" | "neutral" | "negative",
    iconUrl: string;
}