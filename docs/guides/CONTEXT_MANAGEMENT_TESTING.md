# Context Management System - Testing Guide

## Quick Test Plan

### Test 1: Normal Operation (Baseline)
**Goal**: Verify system works normally at <70% context

```bash
# Start fresh COCO
python3 cocoa.py

# Check initial status
/memory status

# Expected: 🟢 Normal status, low percentage
# Example: "Context Window Usage: 🟢 Normal"
# Total Tokens: ~40,000 / 200,000 (20%)
```

**Pass Criteria**: ✅ Green status, no warnings

---

### Test 2: Context Status Visibility
**Goal**: Verify `/memory status` shows all context information

```bash
/memory status
```

**Expected Output**:
```
🧠 Memory & Context Status

**Context Window Usage:** 🟢 Normal
- Total Tokens: XX,XXX / 200,000 (XX.X%)
- System Prompt: ~XX,XXX tokens
- Working Memory: ~XX,XXX tokens
- Identity Context: ~XX,XXX tokens
- Available: XX,XXX tokens

**Adaptive Limits:**
- Warning Threshold: 180,000 tokens (90%)
- Critical Threshold: 190,000 tokens (95%)
- Working Memory Budget: 150,000 tokens

**Recommendations:**
✅ Context usage is healthy - no action needed
```

**Pass Criteria**: ✅ All sections present, no errors

---

### Test 3: Long Conversation Simulation
**Goal**: Trigger emergency compression at 90% threshold

**Method**: Have a very long conversation (200+ exchanges) or manually reduce thresholds for testing

**Option A - Natural Testing** (Recommended):
```bash
# Just keep having a normal conversation
# System will automatically compress when needed
# Watch for yellow warnings around 90% usage
```

**Option B - Accelerated Testing**:
```bash
# Temporarily lower thresholds in .env
CONTEXT_WARNING_THRESHOLD=50000  # Trigger compression earlier
CONTEXT_CRITICAL_THRESHOLD=60000  # Trigger checkpoint earlier
WORKING_MEMORY_MAX_TOKENS=40000   # Smaller working memory

# Restart COCO
python3 cocoa.py

# Have ~50-100 exchanges
# Watch for compression triggers
```

**Expected Behavior at 90%**:
```
⚠️  Context usage: 92.5% (185,000 / 200,000 tokens)
⚠️  Approaching context limit - compressing older memory...
✅ Compressed 150 exchanges into semantic memory
💾 Retained 20 recent exchanges for continuity
✅ Context reduced to 75.3% (150,600 tokens)
```

**Pass Criteria**:
- ✅ Yellow warning shown
- ✅ Compression triggers automatically
- ✅ Context reduced after compression
- ✅ Conversation continuity maintained
- ✅ Information retrievable via `/rag search`

---

### Test 4: Checkpoint Creation
**Goal**: Trigger checkpoint at 95% threshold

**Expected Behavior at 95%**:
```
🚨 Context critical - creating conversation checkpoint...
✅ Conversation checkpoint created!
📝 Summary stored in semantic memory (RAG)
🧠 5 recent exchanges retained for continuity
💾 245 exchanges cleared - context window refreshed
✅ Context reduced to 45.2% (90,400 tokens)
```

**Pass Criteria**:
- ✅ Red alert shown
- ✅ Checkpoint creates automatically
- ✅ Context window refreshed
- ✅ Summary stored in RAG
- ✅ Recent exchanges retained
- ✅ Information retrievable via `/rag search`

---

### Test 5: RAG Integration
**Goal**: Verify compressed/checkpointed information is retrievable

```bash
# After compression or checkpoint, search for information
/rag search <topic from earlier conversation>

# Expected: Information from before compression is retrieved
```

**Example**:
```bash
# Before compression: Discussed "Arizona project architecture"
# After compression occurs
/rag search arizona project

# Expected: RAG returns summary mentioning Arizona project
```

**Pass Criteria**:
- ✅ Information from pre-compression conversation is found
- ✅ RAG retrieval works correctly
- ✅ Summary is coherent and accurate

---

### Test 6: Conversation Continuity
**Goal**: Verify COCO remembers recent context after compression

**After compression/checkpoint**:
```
User: "What were we just discussing?"

Expected: COCO accurately recalls the last 5-20 exchanges
(depending on whether compression or checkpoint occurred)
```

**Pass Criteria**:
- ✅ COCO remembers recent exchanges
- ✅ Responses are contextually appropriate
- ✅ No "I don't remember" responses for recent context

---

### Test 7: No Context Overflow Errors
**Goal**: Ensure no 400 errors occur even in very long conversations

**Method**: Continue conversation past normal overflow point (~2500+ exchanges with old system)

**Pass Criteria**:
- ✅ No Error 400 messages
- ✅ Automatic compressions/checkpoints handle growth
- ✅ Conversation flows naturally
- ✅ No crashes or hangs

---

## Validation Commands

### Check Context Status
```bash
/memory status
```

### Check RAG Stats
```bash
/rag stats
```

### Search RAG for Compressed Content
```bash
/rag search <topic>
```

### View Recent Buffer
```bash
/memory buffer show
```

---

## Expected Metrics

### Token Usage Over Time
- **Start**: ~40K tokens (20%)
- **After 500 exchanges**: ~80K tokens (40%)
- **After 1000 exchanges**: ~140K tokens (70%)
- **After 1500 exchanges**: ~185K tokens (92%) → Compression triggered
- **After compression**: ~150K tokens (75%)
- **After 2000 exchanges**: ~195K tokens (97%) → Checkpoint triggered
- **After checkpoint**: ~90K tokens (45%)

### Compression Events
- **Emergency Compressions**: ~1 per 500 exchanges at default thresholds
- **Checkpoints**: ~1 per 1000 exchanges at default thresholds
- **Cost per Compression**: ~$0.10 (Haiku)
- **Cost per Checkpoint**: ~$0.20 (Haiku)

### Performance
- **Compression Time**: 2-3 seconds
- **Checkpoint Time**: 3-5 seconds
- **Normal Operation Overhead**: <1ms (instant)

---

## Troubleshooting

### If Compression Doesn't Trigger
1. Check context usage with `/memory status`
2. Verify thresholds in `.env` (should be 180K/190K)
3. Check if buffer has enough exchanges (needs >20)
4. Verify ANTHROPIC_API_KEY is set for Haiku

### If Compression Fails
1. Check error message for details
2. Verify internet connection
3. Check Haiku API availability
4. Fallback: Use `/memory buffer clear` manually

### If Checkpoint Fails
1. Verify Simple RAG is initialized (`/rag stats`)
2. Check workspace permissions
3. Check Haiku API availability
4. Fallback: Restart COCO (clears buffer automatically)

### If Information Not Retrieved
1. Check RAG stats: `/rag stats`
2. Verify checkpoint/compression occurred
3. Try broader search terms
4. Check RAG storage with `/rag search <term>`

---

## Stress Test (Optional)

For thorough validation:

```bash
# 1. Start COCO with accelerated thresholds
CONTEXT_WARNING_THRESHOLD=100000
CONTEXT_CRITICAL_THRESHOLD=120000

# 2. Have 500+ exchanges
# 3. Verify multiple compressions occur
# 4. Verify checkpoint occurs
# 5. Verify no errors throughout
# 6. Verify information retrievable
```

**Expected**:
- ✅ 5-10 compressions
- ✅ 2-3 checkpoints
- ✅ No crashes
- ✅ All information in RAG

---

## Success Criteria Summary

✅ **No 400 Context Overflow Errors**
✅ **Automatic Compression Works** (yellow warnings)
✅ **Automatic Checkpoints Work** (red alerts)
✅ **Information Preserved in RAG**
✅ **Conversation Continuity Maintained**
✅ **Status Command Shows All Info**
✅ **Cost Acceptable** (<$2 per 1000 exchanges)
✅ **Performance Acceptable** (<5s overhead)

---

## Reporting Issues

If any test fails:

1. **Check `/memory status`** for current state
2. **Check `/rag stats`** for RAG health
3. **Save error messages** (screenshot or copy)
4. **Note conversation length** (number of exchanges)
5. **Note when compression/checkpoint should have triggered**
6. **Report to development team** with above info

---

## Notes

- Testing with real conversations is recommended over artificial stress tests
- Default thresholds (180K/190K) work well for most use cases
- Lowering thresholds for testing will trigger compressions more frequently
- System is designed to be "set and forget" - testing validates this works
