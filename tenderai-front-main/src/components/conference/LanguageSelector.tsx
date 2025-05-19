import { FC } from 'react';
import { Tabs, Tab } from "@heroui/react";

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
}

export const LanguageSelector: FC<LanguageSelectorProps> = ({
  selectedLanguage,
  onLanguageChange
}) => {
  return (
    <Tabs 
      aria-label="Language Options" 
      selectedKey={selectedLanguage}
      onSelectionChange={(key) => onLanguageChange(String(key))}
    >
      <Tab key="Оригинал" title="Оригинал" />
      <Tab key="Русский" title="Русский" />
      <Tab key="Английский" title="Английский" />
      <Tab key="Испанский" title="Испанский" />
      <Tab key="Китайский" title="Китайский" />
    </Tabs>
  );
};