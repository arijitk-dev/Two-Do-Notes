const nodeCrypto = require("crypto");
if (!nodeCrypto.getRandomValues) nodeCrypto.getRandomValues = nodeCrypto.webcrypto.getRandomValues.bind(nodeCrypto.webcrypto);
if (!globalThis.crypto) globalThis.crypto = nodeCrypto.webcrypto;
