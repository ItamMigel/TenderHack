"use client";

import type { TextAreaProps } from "@heroui/react";

import React from "react";
import { Textarea, cn } from "@heroui/react";


const PromptInput = React.forwardRef<HTMLTextAreaElement, TextAreaProps>(({ classNames = {}, ...props }, ref) => {
    return (
        <Textarea
            ref = {ref}
            aria-label = "Вопрос"
            className = "min-h-[40px] text-primary"
            classNames = {{
                ...classNames,
                label: cn("hidden", classNames?.label),
                input: cn("py-0", classNames?.input),
            }}
            minRows = {1}
            placeholder = "Введите вопрос здесь"
            radius = "lg"
            variant = "bordered"
            {...props}
        />
    );
},);

export default PromptInput;

PromptInput.displayName = "PromptInput";
