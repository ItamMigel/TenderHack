"use client";
import { Button } from "@heroui/react";
import React, { useEffect, useRef, useState } from "react";


export type FileInputProps = {onChange?: (files: object[]) => void}

export default function FileInput (props: FileInputProps) {
    const inputRef = useRef<HTMLInputElement>(null);


    const [processedFileList, setProcessedFileList] = useState([]);

    const [fileList, setFileList] = useState([]);

    useEffect(() => {
        if (inputRef.current) {
            props.onChange(fileList);
        }
    }, [fileList]);

    const handleAddPress = () => {
        if (inputRef.current) {
            inputRef.current.click();
        }
    };

    const handleFileOnChange = (files: FileList) => {
        const fileNames = [];
        const newFilesList = fileList;

        for (const file of files) {
            newFilesList.push(file);

            const splitAr = file.name.split(".");

            const nameBeforeDot = file.name.substring(0, file.name.length - splitAr[splitAr.length - 1].length - 1);
            const name = nameBeforeDot.substring(0, Math.min(10, nameBeforeDot.length)) + "." + splitAr[splitAr.length - 1];

            fileNames.push({ name: name });
        }

        setFileList([...newFilesList]);

        let copy = [...processedFileList];

        copy = copy.concat(fileNames);

        setProcessedFileList(copy);
    };

    const removeFile = (index) => {
        const copy = [...processedFileList];

        const copy2 = [...fileList];
        copy.splice(index, 1);

        copy2.splice(index, 1);


        setProcessedFileList(copy);
        setFileList(copy2);
    };

    return (
        <div>
            <Button className = "mb-3 w-full" onPress = {handleAddPress}>
                <img src = "/icons/file.svg" className = "size-5"/>
                <span>Загрузить файл</span>
            </Button>
            <div className = "space-y-2">
                {processedFileList.map((file, index) => {
                    return <div key = {index} className = "flex gap-x-2 rounded-[8px] bg-[#D4D4D8] bg-opacity-40 px-2 py-1">
                        <div className = "cursor-pointer" onClick = {() => { removeFile(index); }}>Удалить</div>
                        <div className = "text-[14px] font-medium leading-[20px]">{file.name}</div>
                    </div>;
                })}
            </div>

            <input
                type = "file"
                className = "hidden"
                ref = {inputRef}
                data-testid = "uploader"
                onChange = {(e: React.ChangeEvent<HTMLInputElement>) => {
                    handleFileOnChange(e.target.files);
                }}
            />
        </div>

    );
}
