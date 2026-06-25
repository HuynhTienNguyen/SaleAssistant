import PromptSuggestionButton from "./PromptSuggestionButton"
const PromptSeggestionsRow = ({ onPromptClick }) => {
    const prompts = [
        "Tips for analyzing customer behavior and trustworthiness",
        "What should be considered when analyzing customers?",
        "How to communicate effectively with customers."
    ]
    return (
        <div className={"prompt-suggestion-row"}>
            {prompts.map((prompt, index) =>
                <PromptSuggestionButton
                    key={`suggestion-${index}`}
                    text={prompt}
                    onClick={ () => onPromptClick(prompt) }
                />
            )}
        </div>
    )
}

export default PromptSeggestionsRow;