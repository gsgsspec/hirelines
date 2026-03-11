AOS.init({
    duration: 800
});

lucide.createIcons();

document.getElementById('menuBtn').addEventListener('click', function () {
    document.getElementById('mobileMenu').classList.toggle('hidden');
});

const codeLines = [
    [
        { text: "1", class: "text-slate-500" },
        { text: "  async function ", class: "text-brand-accent" },
        { text: "evaluateSystem", class: "text-blue-400" },
        { text: "(nodes: Node[]) {" }
    ],
    [
        { text: "2", class: "text-slate-500" },
        { text: "    const ", class: "text-brand-accent" },
        { text: "results = ", class: "" },
        { text: "await ", class: "text-brand-accent" },
        { text: "Promise.", class: "" },
        { text: "all", class: "text-blue-400" },
        { text: "(nodes.", class: "" },
        { text: "map", class: "text-blue-400" },
        { text: "(n => {" }
    ],
    [
        { text: "3", class: "text-slate-500" },
        { text: "        return ", class: "text-brand-accent" },
        { text: "n.", class: "" },
        { text: "process", class: "text-blue-400" },
        { text: "();" }
    ],
    [
        { text: "4", class: "text-slate-500" },
        { text: "    }));" }
    ]
];

const typingContainer = document.getElementById('typingCode');
const testCases = document.getElementById('testCases');

let lineIndex = 0;
let segmentIndex = 0;
let charIndex = 0;

function resetAnimation() {
    typingContainer.innerHTML = '';
    testCases.innerHTML = '';
    testCases.classList.add('hidden');

    lineIndex = 0;
    segmentIndex = 0;
    charIndex = 0;

    setTimeout(typeNext, 500);
}

function typeNext() {
    if (lineIndex >= codeLines.length) {
        runTests();
        return;
    }

    let lineDiv = typingContainer.children[lineIndex];

    if (!lineDiv) {
        lineDiv = document.createElement('div');
        lineDiv.className = 'flex gap-2 typing-line active';
        typingContainer.appendChild(lineDiv);
    }

    const segment = codeLines[lineIndex][segmentIndex];

    let span = lineDiv.children[segmentIndex];

    if (!span) {
        span = document.createElement('span');
        span.className = segment.class || '';
        lineDiv.appendChild(span);
    }

    if (charIndex < segment.text.length) {
        span.textContent += segment.text[charIndex];
        charIndex++;
        setTimeout(typeNext, 22);
    } else {
        segmentIndex++;
        charIndex = 0;

        if (segmentIndex >= codeLines[lineIndex].length) {
            lineDiv.classList.remove('active');
            lineIndex++;
            segmentIndex = 0;
        }

        setTimeout(typeNext, 22);
    }
}

function runTests() {
    testCases.classList.remove('hidden');

    const running = document.createElement('div');
    running.textContent = 'Running tests...';
    running.className = 'text-yellow-400';
    testCases.appendChild(running);

    setTimeout(() => {
        running.remove();

        const tests = [
            '✓ Test Case 1 Passed',
            '✓ Test Case 2 Passed',
            '✓ Test Case 3 Passed'
        ];

        let i = 0;

        function addTest() {
            if (i < tests.length) {
                const div = document.createElement('div');
                div.textContent = tests[i];
                testCases.appendChild(div);
                i++;
                setTimeout(addTest, 500);
            } else {
                setTimeout(resetAnimation, 2500);
            }
        }

        addTest();
    }, 800);
}

typeNext();


function openDemoForm() {
    const modal = document.getElementById('demoModal');
    const content = document.getElementById('modalContent');

    modal.classList.remove('hidden');
    modal.classList.add('flex');

    setTimeout(() => {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeDemoForm() {
    const modal = document.getElementById('demoModal');
    const content = document.getElementById('modalContent');

    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');

    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }, 300);
}