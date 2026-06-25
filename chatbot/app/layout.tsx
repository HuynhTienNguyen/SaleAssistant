import "./global.css"

export const metadata = {
    title: "chatbotERP",
    description: "introduce of ERP"
}

const RootLayout = ({children}) => {
    return (
        <html lang="en">
        <body>
        {children}
        </body>
        </html>
    )
}

export default RootLayout