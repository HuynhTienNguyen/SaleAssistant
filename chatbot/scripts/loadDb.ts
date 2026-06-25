import { DataAPIClient } from "@datastax/astra-db-ts"
import { PuppeteerWebBaseLoader } from "@langchain/community/document_loaders/web/puppeteer"
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters"
import OpenAI from "openai"
import "dotenv/config"

type SimilarityMetric = "dot_product" | "cosine" | "euclidean"

/**
 * =========================
 * ENV VALIDATION (FAIL FAST)
 * =========================
 */
const getEnv = (key: string): string => {
    const value = process.env[key]
    if (!value) {
        throw new Error(`❌ Missing environment variable: ${key}`)
    }
    return value
}

const OPENAI_API_KEY = getEnv("OPENAI_API_KEY")
const ASTRA_DB_NAMESPACE = getEnv("ASTRA_DB_NAMESPACE")
const ASTRA_DB_COLLECTION = getEnv("ASTRA_DB_COLLECTION")
const ASTRA_DB_API_ENDPOINT = getEnv("ASTRA_DB_API_ENDPOINT")
const ASTRA_DB_APPLICATION_TOKEN = getEnv("ASTRA_DB_APPLICATION_TOKEN")

/*
 * =========================
 * CLIENT SETUP
 * =========================
 */
const openai = new OpenAI({ apiKey: OPENAI_API_KEY })

const client = new DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
const db = client.db(ASTRA_DB_API_ENDPOINT, {
    namespace: ASTRA_DB_NAMESPACE
})

/**
 * =========================
 * DATA CONFIG
 * =========================
 */
const chatbotData = [
    "https://salesmotion.io/blog/b-2-b-sales-methodologies",
    "https://outrageous-ivory-lbst0jdge3.edgeone.app",
    "https://www.researchgate.net/publication/356933292_B_to_B_Sellers'_Skill_Level_in_Sales_Performance_-_Frameworks_and_Findings"
]

const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 512,
    chunkOverlap: 100
})

/**
 * =========================
 * HELPERS
 * =========================
 */
const normalizeUrl = (url: string): string => {
    if (!/^https?:\/\//i.test(url)) {
        return `https://${url}`
    }
    return url
}

/**
 * =========================
 * DB OPERATIONS
 * =========================
 */
const createCollection = async (
    similarityMetric: SimilarityMetric = "cosine"
) => {
    const res = await db.createCollection(ASTRA_DB_COLLECTION, {
        vector: {
            dimension: 1536,
            metric: similarityMetric
        }
    })
    console.log(res)
}

const loadSampleData = async () => {
    const collection = await db.collection(ASTRA_DB_COLLECTION)

    for (const rawUrl of chatbotData) {
        try {
            const url = normalizeUrl(rawUrl)
            console.log(`🔎 Scraping: ${url}`)

            const content = await scrapePage(url)
            if (!content.trim()) {
                console.warn(`⚠️ Empty content, skip: ${url}`)
                continue
            }

            const chunks = await splitter.splitText(content)

            for (const chunk of chunks) {
                const embedding = await openai.embeddings.create({
                    model: "text-embedding-3-small",
                    input: chunk,
                    encoding_format: "float"
                })

                const vector = embedding.data[0].embedding

                await collection.insertOne({
                    $vector: vector,
                    text: chunk,
                    source: url,
                    created_at: new Date().toISOString()
                })
            }
        } catch (err) {
            console.error(`⚠️ Skip URL due to error: ${rawUrl}`)
            console.error(err)
        }
    }
}

/**
 * =========================
 * WEB SCRAPING
 * =========================
 */
const scrapePage = async (url: string): Promise<string> => {
    const loader = new PuppeteerWebBaseLoader(url, {
        launchOptions: {
            headless: true
        },
        gotoOptions: {
            waitUntil: "domcontentloaded"
        },
        evaluate: async (page, browser) => {
            const result = await page.evaluate(() => document.body.innerText)
            await browser.close()
            return result
        }
    })

    return (await loader.scrape()) ?? ""
}

/**
 * =========================
 * ENTRY POINT
 * =========================
 */
;(async () => {
    try {
        try {
            await createCollection()
        } catch {
            console.log("⚠️ Collection already exists, skip creation")
        }

        await loadSampleData()
        console.log("✅ Load DB completed successfully")
        process.exit(0)
    } catch (error) {
        console.error("❌ Load DB failed")
        if (error instanceof Error) {
            console.error(error.message)
            console.error(error.stack)
        } else {
            console.error(error)
        }
        process.exit(1)
    }
})()
