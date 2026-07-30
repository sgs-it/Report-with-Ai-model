import { pipeline, env } from '@xenova/transformers';
import fs from 'fs';
import path from 'path';

env.allowLocalModels = false;
env.useBrowserCache = false;

async function fixCaption() {
    const targetImage = process.argv[2];
    if (!targetImage || !fs.existsSync(targetImage)) {
        console.error("Please provide a valid image path. Example: node fix_caption.js target.jpg");
        process.exit(1);
    }

    console.log("Loading AI model...");
    const extractor = await pipeline('image-feature-extraction', 'Xenova/clip-vit-base-patch32');
    
    console.log(`Extracting embedding for ${targetImage}...`);
    const output = await extractor(targetImage);
    const embedding = Array.from(output.data);
    
    // Normalize
    let sumSq = 0;
    for(let j=0; j<embedding.length; j++) sumSq += embedding[j]*embedding[j];
    let norm = Math.sqrt(sumSq);
    let normalized = embedding.map(x => parseFloat((x / norm).toFixed(4)));

    console.log("Loading database...");
    const dbPath = path.join(process.cwd(), '..', 'custom_knowledge_base.json');
    const database = JSON.parse(fs.readFileSync(dbPath, 'utf-8'));

    let changedCount = 0;
    let matches = [];
    for (let i = 0; i < database.length; i++) {
        let item = database[i];
        
        // Compute cosine similarity
        let dotProduct = 0;
        for (let j = 0; j < normalized.length; j++) {
            dotProduct += normalized[j] * item.embedding[j];
        }
        
        matches.push({score: dotProduct, caption: item.caption, item: item});
    }

    // sort matches by score descending
    matches.sort((a, b) => b.score - a.score);
    console.log("Top 5 matches:");
    for(let i=0; i<5; i++) {
        console.log(`- ${(matches[i].score*100).toFixed(2)}% : ${matches[i].caption}`);
        if (matches[i].score > 0.84) {
            matches[i].item.caption = "Soil Cultivation";
            changedCount++;
        }
    }

    if (changedCount > 0) {
        fs.writeFileSync(dbPath, JSON.stringify(database));
        console.log(`Successfully updated ${changedCount} items in the database to 'Soil Cultivation'!`);
    } else {
        console.log("No closely matching images were found in the database.");
    }
}

fixCaption().catch(console.error);
