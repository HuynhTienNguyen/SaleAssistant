import type { UIMessage } from "ai"

type BubbleProps = {
    message: UIMessage
}

const Bubble = ({ message }: BubbleProps) => {
    const { role, parts } = message

    const text = parts
        .filter((part) => part.type === "text")
        .map((part) => part.text)
        .join("")

    return (
        <div className={`${role} bubble`} style={{ whiteSpace: 'pre-wrap' }}>
            {text}
        </div>
    )
}

export default Bubble

