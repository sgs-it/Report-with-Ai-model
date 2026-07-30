import { pipeline, env } from '@xenova/transformers';
import fs from 'fs';
import path from 'path';

env.allowLocalModels = false;
env.useBrowserCache = false;

const datasetPath = path.join(process.cwd(), 'dataset', 'dataset.json');
const dataset = JSON.parse(fs.readFileSync(datasetPath, 'utf-8'));

async function buildDatabase() {
    console.log("Loading CLIP Vision model...");
    const extractor = await pipeline('image-feature-extraction', 'Xenova/clip-vit-base-patch32');
    
    console.log(`Model loaded. Processing ${dataset.length} images...`);
    const database = [];
    
    for (let i = 0; i < dataset.length; i++) {
        const item = dataset[i];
        const imgPath = path.join(process.cwd(), 'dataset', item.image);
        
        if (!fs.existsSync(imgPath)) {
            continue;
        }
        
        console.log(`[${i+1}/${dataset.length}] Extracting embedding for ${item.image}`);
        try {
            const output = await extractor(imgPath);
            const embedding = Array.from(output.data);
            
            // Normalize embedding for cosine similarity later
            let sumSq = 0;
            for(let j=0; j<embedding.length; j++) sumSq += embedding[j]*embedding[j];
            let norm = Math.sqrt(sumSq);
            let normalized = embedding.map(x => parseFloat((x / norm).toFixed(4)));
            
            database.push({
                caption: item.caption,
                embedding: normalized
            });
        } catch (e) {
            console.error(`Error processing ${item.image}:`, e);
        }
    }
    
    const outPath = path.join(process.cwd(), '..', 'custom_knowledge_base.json');
    fs.writeFileSync(outPath, JSON.stringify(database));
    console.log(`Done! Saved ${database.length} items to custom_knowledge_base.json`);
}

buildDatabase().catch(console.error);
