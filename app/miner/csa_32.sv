module csa_32 (
    input  logic [31:0] a,
    input  logic [31:0] b,
    input  logic [31:0] c,
    output logic [31:0] sum,
    output logic [31:0] carry
);
    genvar i;
    generate
        for (i = 0; i < 32; i++) begin : gen_csa
            assign sum[i]   = a[i] ^ b[i] ^ c[i];
            assign carry[i] = (a[i] & b[i]) | (b[i] & c[i]) | (a[i] & c[i]);
        end
    endgenerate
endmodule
