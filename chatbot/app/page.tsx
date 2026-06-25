"use client"
import Image from "next/image"
import { useState } from "react"
import chatbotERP_logo from "./assets/chatbotERP_Logo.png"
import { useChat } from "@ai-sdk/react"
import Bubble from "./components/Bubble"
import LoadingBubble from "./components/LoadingBubble"
import PromptSuggestionsRow from "./components/PromptSuggestionsRow"

const Home = () => {
    const [input, setInput] = useState("")

    const {
        messages,
        sendMessage,
        status,
        error
    } = useChat()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim()) return

        await sendMessage({ text: input })
        setInput("")
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e as any)
        }
    }

    const handlePrompt = async (promptText: string) => {
        await sendMessage({ text: promptText })
    }

    const noMessages = messages.length === 0
    const isLoading = status === "submitted" || status === "streaming"

    return (
        <main>
            <Image src={chatbotERP_logo} width={250} alt="chatbotERP Logo"/>

            <section className={noMessages ? "" : "populated"}>
                {noMessages ? (
                    <>
                        <p className="starter-text">
                            Welcome to ERP chatbot!!!
                            Feel free to ask any questions about ERP.
                            We hope you enjoy!
                        </p>
                        <br />
                        <PromptSuggestionsRow onPromptClick={handlePrompt} />
                    </>
                ) : (
                    <>
                        {messages.map((message) => (
                            <Bubble key={message.id} message={message} />
                        ))}
                        {isLoading && <LoadingBubble />}
                    </>
                )}

                {error && <div className="error">{error.message}</div>}
            </section>

            <form onSubmit={handleSubmit}>
                <textarea
                    className="question-box"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask me something..."
                    disabled={isLoading}
                    rows={1}
                />
                <input type="submit" value="Send" disabled={isLoading} />
            </form>
        </main>
    )
}

export default Home