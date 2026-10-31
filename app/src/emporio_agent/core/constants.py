"""Parametros de negocio extraidos do manual de politicas.

Responsabilidade: fonte unica dos numeros da loja (descontos, prazos, frete,
horario). As regras em core/rules usam estes valores, nunca numeros soltos.

Pode importar de: biblioteca padrao.
Nao deve importar de: nenhum outro modulo do projeto.
Fase de implementacao: F0 (pronto), revisar na F2
"""

STORE_TIMEZONE = "America/Campo_Grande"
STORE_ADDRESS = "Rua 14 de Maio, 3200, Centro, Campo Grande-MS"
STORE_POSTAL_CODE = "79202-333"
STORE_PHONE = "(67) 3341-4444"
STORE_WHATSAPP = "(67) 3321-4500"
STORE_EMAIL = "contato@emporiodamusica.com.br"

PIX_DISCOUNT_PERCENT = 5

FREE_SHIPPING_MIN_BRL = 500
LOCAL_SHIPPING_FEE_BRL = 35

RETURN_WINDOW_DAYS = 7
DEFECT_EXCHANGE_DAYS = 30
LEGAL_WARRANTY_DAYS = 90
REFUND_BUSINESS_DAYS = 10

# (parcelas_max, parcela_minima_brl). Ver suposicoes 3 e 4 do documento do projeto.
INSTALLMENT_TIERS = ((3, 50), (6, 80), (12, 100))
SPLIT_PAYMENT_MIN_BRL = 2000
BOLETO_SETTLEMENT_BUSINESS_DAYS = 3

COMPLAINT_RETURN_BUSINESS_HOURS = 24

# Horários confirmados no manual de políticas; intervalo [abertura, fechamento).
STORE_WEEKDAY_HOURS = (9, 18)
STORE_SATURDAY_HOURS = (9, 13)
STORE_SUNDAY_HOURS = None

# Região metropolitana: valores fixos se aplicam somente em Campo Grande.
METROPOLITAN_CITIES = ("Campo Grande",)
OVERSIZED_NAME_TERMS = ("bateria", "piano", "contrabaixo")
OUT_OF_TOWN_SHIPPING_OPTIONS = {
    "PAC": (5, 12),
    "SEDEX": (2, 5),
    "Jadlog": (3, 8),
}

