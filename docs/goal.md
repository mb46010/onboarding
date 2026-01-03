# Mock MCP tools available
async def check_equipment_order(employee_email: str) -> dict:
    """Returns: {laptop: bool, monitor: bool, headset: bool, status: str}"""
    
async def schedule_meeting(employee_email: str, manager_email: str, 
                          duration_mins: int) -> dict:
    """Returns: {meeting_id: str, scheduled_time: str, calendar_link: str}"""

# Documents (3 PDFs ingested in vector store)
- offer_letter_template.pdf
- equipment_policy.pdf  
- first_week_schedule.pdf
```

### **Your Task**
Build a **LangGraph workflow agent** that:

1. **Intent classification node**: Determine if query needs:
   - Document retrieval only
   - Equipment check
   - Meeting scheduling
   - Combination of above

2. **Parallel execution**: If query needs equipment check + doc retrieval, run in parallel

3. **Response synthesis**: Combine results into helpful answer

### **Example Queries to Handle**
```
"What equipment will I get?"
→ Retrieve equipment policy + check equipment order status

"When is my first day and has my laptop been ordered?"
→ Retrieve schedule + check equipment (parallel)

"Can you schedule my first 1:1 with sarah@company.com?"
→ Schedule meeting + confirm via response