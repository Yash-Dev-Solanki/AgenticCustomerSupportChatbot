using AgenticAPI.Application.CreateCustomer;
using AgenticAPI.Domain;
using AutoMapper;

namespace AgenticAPI.Infrastructure
{
    public class MapperProfile: Profile
    {
        public MapperProfile() 
        {
            CreateMap<CreateCustomerRawRequestModel, Customer>()
                .ForMember(dest => dest.PaymentMethod, opt => opt.MapFrom(src => src.PaymentMethod.ToString()))
                .ReverseMap();
        }
    }
}
