import fs from 'fs';

console.log("Loading mapping.json...");
const mapping = JSON.parse(fs.readFileSync('mapping.json', 'utf-8'));

console.log("Loading custom_knowledge_base.json...");
const db = JSON.parse(fs.readFileSync('../custom_knowledge_base.json', 'utf-8'));

console.log(`Original DB size: ${db.length}`);

// Step 1: Full Re-categorization (Apply mapping & remove garbage)
let mappedDb = [];
let unmappedCount = 0;

for (let item of db) {
    let raw = item.caption;
    if (mapping[raw]) {
        item.caption = mapping[raw];
        mappedDb.push(item);
    } else {
        unmappedCount++;
    }
}

console.log(`Mapped ${mappedDb.length} items. Dropped ${unmappedCount} garbage images (logos, dates, typos).`);

// Step 2: Safe Cleanup (Majority Rules for identical images)
console.log("Running Safe Cleanup (Majority Rules)...");
let uniqueEmbeddings = new Map(); // key -> array of captions

for (let item of mappedDb) {
    // We round to 2 decimal places to group highly similar embeddings
    let key = item.embedding.map(x => x.toFixed(2)).join(',');
    if (!uniqueEmbeddings.has(key)) {
        uniqueEmbeddings.set(key, []);
    }
    uniqueEmbeddings.get(key).push(item.caption);
}

// Find majority caption for each group
let majorityMap = new Map();
let conflictResolutions = 0;

for (let [key, captions] of uniqueEmbeddings.entries()) {
    let counts = {};
    for (let c of captions) counts[c] = (counts[c] || 0) + 1;
    
    let sorted = Object.entries(counts).sort((a,b) => b[1] - a[1]);
    let majority = sorted[0][0];
    majorityMap.set(key, majority);
    
    if (sorted.length > 1) {
        conflictResolutions += (captions.length - sorted[0][1]);
    }
}

// Apply majority rules
let finalDb = [];
let finalSet = new Set(); // to remove exact duplicates
for (let item of mappedDb) {
    let key = item.embedding.map(x => x.toFixed(2)).join(',');
    let newCaption = majorityMap.get(key);
    item.caption = newCaption;
    
    // Deduplicate exact embeddings to shrink file size!
    if (!finalSet.has(key)) {
        finalSet.add(key);
        finalDb.push(item);
    }
}

console.log(`Resolved ${conflictResolutions} conflicting captions using Majority Rules.`);
console.log(`Deduplicated dataset down to ${finalDb.length} unique images for maximum speed.`);

fs.writeFileSync('../custom_knowledge_base.json', JSON.stringify(finalDb));
console.log("Successfully overwrote custom_knowledge_base.json!");
