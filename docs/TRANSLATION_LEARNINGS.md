# Translation Learnings for Reflow

## SMB Migration Case Study: C++ (NES Decompilation) to Python

### Critical Insight: Language Abstraction Levels

**Before attempting ANY code translation, consider the abstraction hierarchy:**

```
Level 1: Machine Code      → Binary (0s and 1s), CPU-specific
Level 2: Assembly          → Mnemonics (ADD, MOV, JMP), hardware-aware
Level 3: Middle-level      → C, C++ - high-level constructs + memory access
Level 4: High-level        → Python, Java, C# - abstracts hardware entirely
```

**The SMB source code represents THREE abstraction levels:**
1. Original NES ROM → Machine code (6502 binary)
2. Decompiled ASM → Assembly (6502 mnemonics)
3. SMB.cpp → Middle-level C++ that *mimics* assembly

**Our mistake**: We tried to translate level 2-3 patterns directly to level 4 (Python).

**The correct approach**: Identify what **high-level operation** each low-level pattern represents, then use the target language's native abstraction for that operation.

### Translation Hierarchy Principle

Before translating, ask: **"What does this code DO, not HOW does it do it?"**

| Source Pattern (C++/ASM) | What It Does | Python Equivalent |
|--------------------------|--------------|-------------------|
| `a = M(PlayerState); a &= 0x03; if(z) goto...` | Check if player is in state X | `if player.state == State.X:` |
| `++M(Score); ++M(Score+1); if(c) ++M(Score+2)` | Add to 24-bit score | `score += points` |
| `M(0x200 + x) = a; ++x; if(x != 64) goto loop` | Copy 64 bytes to sprite RAM | `sprites = data.copy()` |
| `JSR(DrawTile, 5); goto Return` | Draw a tile | `renderer.draw_tile(...)` |
| `a <<= 1; a \|= M(Random); M(Random) = a` | Generate random number | `random.randint(...)` |

### Abstraction Level Mapping Rules

**Rule 1: Memory Operations → Object Properties**
```cpp
// Middle-level (C++ mimicking ASM)
M(Player_X_Position) = a;
a = M(Player_State);
++M(FrameCounter);
```
```python
# High-level (Python)
player.x = value
state = player.state
frame_counter += 1
```

**Rule 2: Bit Manipulation → Boolean/Enum**
```cpp
// Middle-level
a = M(PlayerStatus);
a &= BOOST_BINARY(00000100);  // Check fire flower bit
if (!z) goto HasFireFlower;
```
```python
# High-level
if player.powerup == Powerup.FIRE:
```

**Rule 3: Loops with Counters → Iterators/Comprehensions**
```cpp
// Middle-level
x = 0;
Loop:
  M(Dest + x) = M(Src + x);
  ++x;
  if (x != count) goto Loop;
```
```python
# High-level
dest = src.copy()
# or
for i, val in enumerate(src):
    dest[i] = val
```

**Rule 4: State Machines with goto → Classes/Methods**
```cpp
// Middle-level
PlayerMovement:
  if (jumping) goto HandleJump;
  if (falling) goto HandleFall;
  goto HandleWalk;
```
```python
# High-level
def update_player(self):
    match self.state:
        case State.JUMPING: self.handle_jump()
        case State.FALLING: self.handle_fall()
        case _: self.handle_walk()
```

**Rule 5: Hardware Register Writes → API Calls**
```cpp
// Middle-level (NES hardware)
writeData(PPU_CTRL_REG1, a);
writeData(PPU_SCROLL, x);
writeData(PPU_SCROLL, y);
```
```python
# High-level (Pygame)
pygame.display.set_mode(...)
screen.scroll(x, y)
```

### Pre-Translation Analysis Workflow

**Step 1: Classify Source Abstraction Level**
- Is it assembly-like? (registers, flags, goto)
- Is it middle-level? (pointers, memory addresses, bit ops)
- Is it already high-level? (classes, methods, abstractions)

**Step 2: Identify Semantic Clusters**
Group related low-level operations into high-level concepts:
- "These 20 lines manage player jumping" → `player.jump()`
- "These 50 lines render a tile row" → `renderer.draw_row()`
- "These 100 lines handle enemy AI" → `enemy.update()`

**Step 3: Map to Target Language Idioms**
- Memory arrays → Dataclasses/Objects
- Bit flags → Enums/Booleans
- goto-based flow → Methods/Match statements
- Hardware I/O → Framework APIs

**Step 4: Implement Top-Down**
Start with high-level structure, fill in details:
```python
class Game:
    def update(self):
        self.player.update()
        self.enemies.update()
        self.level.update()

    def render(self):
        self.level.draw()
        self.player.draw()
        self.enemies.draw()
```

### Key Insight: Semantic vs Literal Translation

**Problem Discovered**: Initial approach was too literal - we tried to replicate every 6502 CPU operation (registers, flags, memory addresses) in Python. This led to:
- 7,862 low-level operations across 1,654 states
- Complex flag dependency tracking (carry, zero, negative, overflow)
- PPU/APU hardware emulation that would be replaced anyway
- Difficult-to-debug state machine with hardware-level semantics

**Solution: Semantic Translation**
Instead of translating assembly-level operations, translate the **high-level game logic**:

```
WRONG (Literal):
  a = M(PlayerState)     →  self.e.a.set(self.e.read(0x001E))
  a &= 0x03              →  self.e.a.set(self.e.a.value & 0x03)
  if (z) goto Standing   →  if self.e.z: return 'Standing'

RIGHT (Semantic):
  if player.state == PlayerState.STANDING:
      handle_standing_player()
```

### Translation Strategy for Reflow

#### Phase 1: Identify Semantic Components
1. **Game State Variables** - What data represents game state?
   - Player position, velocity, state (standing, jumping, running)
   - Enemy positions, types, states
   - Level data, scroll position
   - Score, lives, time, coins

2. **Game Logic Functions** - What are the high-level behaviors?
   - `handle_player_input()` - Process controller input
   - `update_player_physics()` - Gravity, movement
   - `check_collisions()` - Player vs enemies, blocks
   - `update_enemies()` - Enemy AI and movement
   - `render_frame()` - Draw current game state

3. **Rendering** - Target platform native rendering
   - Don't emulate PPU/VRAM - use Pygame directly
   - Sprite sheets instead of CHR ROM
   - Direct pixel manipulation instead of nametables

#### Phase 2: Map Source to Semantic Components
For each source file section:
1. Identify what game behavior it implements
2. Extract the logic, not the implementation
3. Translate to idiomatic target language

Example mapping from SMB.cpp:
```
Source Label          → Semantic Function
--------------          ------------------
PlayerMovementSubs    → player.update_movement()
EnemyMovementSubs     → enemy.update_movement()
PlayerCollisionSubs   → collision.check_player()
DrawTitleScreen       → ui.draw_title_screen()
```

#### Phase 3: Data Structure Design
Design proper data structures instead of flat memory arrays:

```python
# Instead of memory addresses:
# M(0x001E) = Player_State
# M(0x0086) = Player_X_Position

# Use proper classes:
@dataclass
class Player:
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    state: PlayerState
    facing: Direction
    is_big: bool
    has_fire: bool
```

### Indicators That Literal Translation is Wrong

Watch for these red flags:
1. **Emulating CPU flags** (carry, zero, negative) - These are implementation details
2. **Bit manipulation for state** - Use enums and booleans instead
3. **Memory address constants** - Use named fields in classes
4. **Hardware register writes** - Replace with native API calls
5. **Assembly idioms** (JSR/RTS, stack manipulation) - Use function calls

### Reflow Tool Recommendations

#### New Tool: `analyze_abstraction_level.py`
**First step before any translation**: Classify the source code's abstraction level.

```python
# Output example:
{
    "abstraction_level": "middle",  # low/middle/high
    "indicators": {
        "has_memory_addresses": true,
        "has_cpu_registers": true,
        "has_goto_statements": true,
        "has_bit_manipulation": true,
        "has_hardware_io": true,
        "has_classes": false,
        "has_high_level_types": false
    },
    "recommendation": "semantic_translation",
    "target_abstraction_gap": 2  # levels between source and target
}
```

**When gap >= 2**: Don't translate 1:1. Use semantic clustering.

#### New Tool: `analyze_semantic_structure.py`
Given a legacy codebase, identify:
- State variables (frequently read/written memory locations)
- Function boundaries (labels that are JSR targets)
- Logical groupings (related labels that form a subsystem)
- **Semantic clusters**: Groups of low-level ops that form one high-level operation

#### New Tool: `generate_semantic_stubs.py`
Generate high-level Python class stubs from semantic analysis:
```python
class PlayerController:
    """Handles player input and state changes."""

    def handle_input(self, buttons: ControllerState) -> None:
        """Process controller input for player."""
        # TODO: Translate from PlayerMovementSubs
        pass
```

#### New Tool: `identify_encapsulation_opportunities.py`
Find patterns where multiple low-level operations can become one high-level call:

```
Input:  a = M(X); a &= 0xFF; a >>= 4; M(Y) = a
Output: "Extract high nibble from X, store in Y"
        → y = (x >> 4) & 0x0F
        → Or if semantic: status = get_status_flags(data)
```

#### Updated Workflow Step: LM-03 (Translation Rules)
Add abstraction level analysis BEFORE defining translation rules:

1. **Analyze abstraction levels** of source and target languages
2. **Calculate abstraction gap** (e.g., ASM→Python = 3 levels)
3. **If gap >= 2**: Define semantic clusters, not 1:1 mappings
4. **If gap == 1**: Direct translation may work (C++ → Java)
5. **If gap == 0**: Mostly syntax changes (Python 2 → Python 3)

#### Updated Workflow Step: LM-05 (Complete Code Translation)
Add decision point:
1. Is source low-level/hardware-specific? → Use Semantic Translation
2. Is source already high-level? → Use Direct Translation
3. Mixed? → Identify layers, translate appropriately

### Metrics for Semantic Translation

Track these to measure translation quality:
- **Lines of code ratio**: Target should be 10-50% of source (semantic is more concise)
- **Test coverage**: Behavioral tests, not implementation tests
- **Cyclomatic complexity**: Should decrease, not increase
- **Runtime dependencies**: Fewer hardware emulation deps

### SMB-Specific Semantic Components

For this game specifically:

```
High-Level Components:
├── GameEngine
│   ├── game_loop()
│   ├── update(delta_time)
│   └── render()
├── Player
│   ├── handle_input()
│   ├── update_physics()
│   ├── check_collisions()
│   └── render()
├── Level
│   ├── load(world, area)
│   ├── get_tile(x, y)
│   ├── scroll(offset)
│   └── render()
├── EnemyManager
│   ├── spawn_enemies()
│   ├── update_all()
│   └── render_all()
├── UI
│   ├── draw_hud()
│   ├── draw_title_screen()
│   └── draw_game_over()
└── Audio
    ├── play_music()
    └── play_sfx()
```

### Next Steps for SMB Migration

1. **Define semantic data structures** - Player, Enemy, Level, Tile classes
2. **Map source labels to semantic functions** - Create mapping document
3. **Implement core game loop** - Frame update, render cycle
4. **Translate player controller first** - Most visible/testable
5. **Add level rendering** - Use tile-based approach with Pygame
6. **Implement enemy behavior** - One type at a time
7. **Add collision detection** - Player-enemy, player-block
8. **Polish with audio and UI**

### Conclusion

The data-driven state machine approach (1,654 states, 7,862 operations) was an interesting experiment but ultimately the wrong abstraction for this translation. The semantic approach will produce:
- Cleaner, more maintainable code
- Easier debugging (game concepts, not CPU flags)
- Natural use of Python features (classes, methods, type hints)
- Decoupling from NES hardware specifics
